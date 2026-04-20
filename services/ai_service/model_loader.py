from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any
import warnings

import joblib
import numpy as np

from app_config import Settings
from schemas import BehaviorInput


CLASS_SCORE_MAP = {
    "low_intent": 0.20,
    "medium_intent": 0.55,
    "high_intent": 0.90,
}


@dataclass
class PredictionResult:
    label: str
    confidence: float
    score: float
    explanation: str
    probabilities: dict[str, float]


@dataclass
class ArtifactModelBundle:
    model_path: Path
    scaler_path: Path
    label_encoder_path: Path
    metrics_path: Path
    model: Any = None
    scaler: Any = None
    label_encoder: Any = None
    metrics: dict[str, Any] = field(default_factory=dict)
    best_model_name: str | None = None
    feature_columns: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    load_error: str | None = None
    backend: str = "heuristic_fallback"

    @classmethod
    def from_settings(cls, settings: Settings) -> "ArtifactModelBundle":
        bundle = cls(
            model_path=settings.model_path,
            scaler_path=settings.scaler_path,
            label_encoder_path=settings.label_encoder_path,
            metrics_path=settings.metrics_path,
        )
        bundle.load()
        return bundle

    @property
    def is_ready(self) -> bool:
        return self.model is not None and self.scaler is not None and self.label_encoder is not None

    def summary(self) -> dict[str, Any]:
        return {
            "backend": self.backend,
            "ready": self.is_ready,
            "best_model": self.best_model_name,
            "feature_columns": self.feature_columns,
            "classes": self.classes,
            "load_error": self.load_error,
        }

    def load(self) -> None:
        missing_paths = [
            str(path)
            for path in [self.model_path, self.scaler_path, self.label_encoder_path]
            if not path.exists()
        ]
        if missing_paths:
            self.load_error = f"Missing artifact files: {', '.join(missing_paths)}"
            return

        if self.metrics_path.exists():
            try:
                self.metrics = json.loads(self.metrics_path.read_text(encoding="utf-8"))
                self.best_model_name = self.metrics.get("best_model")
            except Exception as exc:
                self.load_error = f"Could not read metrics summary: {exc}"

        try:
            from tensorflow.keras.models import load_model
        except Exception as exc:
            self.load_error = f"TensorFlow unavailable for artifact inference: {exc}"
            return

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.scaler = joblib.load(self.scaler_path)
                self.label_encoder = joblib.load(self.label_encoder_path)
            self.model = load_model(self.model_path, compile=False)
        except Exception as exc:
            self.model = None
            self.scaler = None
            self.label_encoder = None
            self.load_error = f"Could not load AI artifacts: {exc}"
            return

        metrics_feature_columns = self.metrics.get("feature_columns", []) if self.metrics else []
        scaler_feature_columns = list(getattr(self.scaler, "feature_names_in_", []))
        self.feature_columns = list(metrics_feature_columns or scaler_feature_columns)
        self.classes = list(self.metrics.get("classes", []) or getattr(self.label_encoder, "classes_", []).tolist())
        self.backend = "artifact_model"
        self.load_error = None

    def predict(self, behavior: BehaviorInput) -> PredictionResult:
        if not self.is_ready:
            raise RuntimeError(self.load_error or "Artifact model bundle is not ready.")

        feature_columns = self.feature_columns or [
            "search_count",
            "product_view_count",
            "detail_view_count",
            "dwell_time_sec",
            "add_wishlist_count",
            "add_to_cart_count",
            "remove_from_cart_count",
            "purchase_count",
        ]

        values = np.array([[float(getattr(behavior, feature)) for feature in feature_columns]], dtype="float32")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            scaled = self.scaler.transform(values)
        sequence = scaled.reshape((1, len(feature_columns), 1))
        probabilities = self.model.predict(sequence, verbose=0)[0]

        predicted_index = int(np.argmax(probabilities))
        predicted_label = str(self.label_encoder.inverse_transform([predicted_index])[0])
        class_labels = self.classes or [str(label) for label in getattr(self.label_encoder, "classes_", [])]
        probability_map = {
            label: float(probabilities[index])
            for index, label in enumerate(class_labels)
        }
        confidence = float(probabilities[predicted_index])
        score = sum(probability_map[label] * CLASS_SCORE_MAP.get(label, 0.5) for label in probability_map)
        explanation = (
            f"Artifact-backed {self.best_model_name or 'sequential'} model predicted "
            f"{predicted_label} with {confidence * 100:.1f}% confidence."
        )

        return PredictionResult(
            label=predicted_label,
            confidence=round(confidence, 3),
            score=round(float(score), 3),
            explanation=explanation,
            probabilities={label: round(value, 4) for label, value in probability_map.items()},
        )
