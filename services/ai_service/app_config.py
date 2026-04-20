from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def resolve_dataset_path() -> Path:
    dataset_path = Path(os.getenv("AI_DATASET_PATH", "data/data_user500.csv"))
    if dataset_path.is_absolute():
        return dataset_path
    return (BASE_DIR / dataset_path).resolve()


@dataclass(frozen=True)
class Settings:
    service_name: str = "novamarket-ai-service"
    dataset_path: Path = resolve_dataset_path()
    artifacts_dir: Path = Path(os.getenv("AI_ARTIFACTS_DIR", (BASE_DIR / "artifacts").as_posix()))
    model_path: Path = Path(os.getenv("AI_MODEL_PATH", (BASE_DIR / "artifacts" / "model_best.keras").as_posix()))
    scaler_path: Path = Path(os.getenv("AI_SCALER_PATH", (BASE_DIR / "artifacts" / "scaler.pkl").as_posix()))
    label_encoder_path: Path = Path(
        os.getenv("AI_LABEL_ENCODER_PATH", (BASE_DIR / "artifacts" / "label_encoder.pkl").as_posix())
    )
    metrics_path: Path = Path(
        os.getenv("AI_METRICS_PATH", (BASE_DIR / "artifacts" / "metrics_summary.json").as_posix())
    )
    product_service_url: str = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8010")
    request_timeout_seconds: float = float(os.getenv("AI_REQUEST_TIMEOUT", "6"))
    max_recommendations: int = int(os.getenv("AI_MAX_RECOMMENDATIONS", "4"))
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "novamarket123")
    neo4j_auto_sync: bool = os.getenv("AI_GRAPH_AUTO_SYNC", "1").lower() in {"1", "true", "yes", "on"}


settings = Settings()
