from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent


ROOT_DIR = Path(__file__).resolve().parents[2]
NOTEBOOK_PATH = ROOT_DIR / "ai_service" / "notebooks" / "train_rnn_lstm_bilstm.ipynb"


def markdown_cell(source: str) -> dict:
    normalized = dedent(source).strip()
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in normalized.splitlines()],
    }


def code_cell(source: str) -> dict:
    normalized = dedent(source).strip()
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in normalized.splitlines()],
    }


def build_notebook() -> dict:
    cells = [
        markdown_cell(
            """
            # Train RNN, LSTM, biLSTM for NovaMarket AI Service

            Notebook này scaffold sẵn pipeline train cho bài AI Service:
            - đọc `data_user500.csv`,
            - chuẩn hóa 8 hành vi,
            - train `RNN`, `LSTM`, `biLSTM`,
            - so sánh metrics,
            - lưu `model_best.keras`, `scaler.pkl`, `label_encoder.pkl`.
            """
        ),
        code_cell(
            """
            from pathlib import Path
            import json
            import warnings

            import joblib
            import matplotlib.pyplot as plt
            import numpy as np
            import pandas as pd
            import seaborn as sns
            from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import LabelEncoder, MinMaxScaler
            from tensorflow.keras import Sequential, Input
            from tensorflow.keras.callbacks import EarlyStopping
            from tensorflow.keras.layers import Bidirectional, Dense, Dropout, LSTM, SimpleRNN

            warnings.filterwarnings("ignore")
            sns.set_theme(style="whitegrid")

            DATASET_PATH = Path("/kaggle/input/Dataset/data_user500.csv")
            ARTIFACTS_DIR = Path("/kaggle/working/artifacts")
            ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

            FEATURE_COLUMNS = [
                "search_count",
                "product_view_count",
                "detail_view_count",
                "dwell_time_sec",
                "add_wishlist_count",
                "add_to_cart_count",
                "remove_from_cart_count",
                "purchase_count",
            ]
            TARGET_COLUMN = "target_label"
            RANDOM_STATE = 42
            """
        ),
        code_cell(
            """
            df = pd.read_csv(DATASET_PATH)
            df.head(20)
            """
        ),
        code_cell(
            """
            print(df[TARGET_COLUMN].value_counts())
            print(df[FEATURE_COLUMNS].describe().T)
            """
        ),
        code_cell(
            """
            X = df[FEATURE_COLUMNS].copy()
            y = df[TARGET_COLUMN].copy()

            scaler = MinMaxScaler()
            X_scaled = scaler.fit_transform(X)

            label_encoder = LabelEncoder()
            y_encoded = label_encoder.fit_transform(y)

            X_train, X_temp, y_train, y_temp = train_test_split(
                X_scaled,
                y_encoded,
                test_size=0.30,
                random_state=RANDOM_STATE,
                stratify=y_encoded,
            )

            X_val, X_test, y_val, y_test = train_test_split(
                X_temp,
                y_temp,
                test_size=0.50,
                random_state=RANDOM_STATE,
                stratify=y_temp,
            )

            X_train_seq = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
            X_val_seq = X_val.reshape((X_val.shape[0], X_val.shape[1], 1))
            X_test_seq = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

            print("Train:", X_train_seq.shape, y_train.shape)
            print("Val:", X_val_seq.shape, y_val.shape)
            print("Test:", X_test_seq.shape, y_test.shape)
            """
        ),
        code_cell(
            """
            def build_rnn(input_shape, num_classes):
                model = Sequential([
                    Input(shape=input_shape),
                    SimpleRNN(64),
                    Dropout(0.20),
                    Dense(32, activation="relu"),
                    Dense(num_classes, activation="softmax"),
                ])
                model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
                return model

            def build_lstm(input_shape, num_classes):
                model = Sequential([
                    Input(shape=input_shape),
                    LSTM(64),
                    Dropout(0.20),
                    Dense(32, activation="relu"),
                    Dense(num_classes, activation="softmax"),
                ])
                model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
                return model

            def build_bilstm(input_shape, num_classes):
                model = Sequential([
                    Input(shape=input_shape),
                    Bidirectional(LSTM(64)),
                    Dropout(0.30),
                    Dense(32, activation="relu"),
                    Dense(num_classes, activation="softmax"),
                ])
                model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
                return model
            """
        ),
        code_cell(
            """
            MODEL_BUILDERS = {
                "RNN": build_rnn,
                "LSTM": build_lstm,
                "biLSTM": build_bilstm,
            }

            histories = {}
            metrics_summary = {}
            trained_models = {}

            for model_name, builder in MODEL_BUILDERS.items():
                model = builder((len(FEATURE_COLUMNS), 1), len(label_encoder.classes_))
                history = model.fit(
                    X_train_seq,
                    y_train,
                    validation_data=(X_val_seq, y_val),
                    epochs=35,
                    batch_size=32,
                    callbacks=[EarlyStopping(monitor="val_loss", patience=6, restore_best_weights=True)],
                    verbose=1,
                )

                predictions = model.predict(X_test_seq, verbose=0)
                y_pred = predictions.argmax(axis=1)
                precision, recall, f1, _ = precision_recall_fscore_support(
                    y_test,
                    y_pred,
                    average="macro",
                    zero_division=0,
                )
                loss, accuracy = model.evaluate(X_test_seq, y_test, verbose=0)

                histories[model_name] = history.history
                trained_models[model_name] = model
                metrics_summary[model_name] = {
                    "accuracy": float(accuracy),
                    "loss": float(loss),
                    "macro_precision": float(precision),
                    "macro_recall": float(recall),
                    "macro_f1": float(f1),
                }

            metrics_summary
            """
        ),
        code_cell(
            """
            best_model_name = max(metrics_summary, key=lambda name: metrics_summary[name]["macro_f1"])
            best_model = trained_models[best_model_name]
            print("Best model:", best_model_name)
            print(json.dumps(metrics_summary[best_model_name], indent=2))
            """
        ),
        code_cell(
            """
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))

            for model_name, history in histories.items():
                axes[0].plot(history["loss"], label=f"{model_name} train")
                axes[0].plot(history["val_loss"], linestyle="--", label=f"{model_name} val")
                axes[1].plot(history["accuracy"], label=f"{model_name} train")
                axes[1].plot(history["val_accuracy"], linestyle="--", label=f"{model_name} val")

            axes[0].set_title("Loss curves")
            axes[1].set_title("Accuracy curves")
            axes[0].legend()
            axes[1].legend()
            plt.tight_layout()
            plt.show()
            """
        ),
        code_cell(
            """
            comparison_df = pd.DataFrame(metrics_summary).T.sort_values("macro_f1", ascending=False)
            comparison_df[["accuracy", "macro_precision", "macro_recall", "macro_f1"]].plot(
                kind="bar",
                figsize=(10, 5),
                title="Model comparison",
            )
            plt.xticks(rotation=0)
            plt.tight_layout()
            plt.show()
            """
        ),
        code_cell(
            """
            best_predictions = best_model.predict(X_test_seq, verbose=0).argmax(axis=1)
            cm = confusion_matrix(y_test, best_predictions)

            plt.figure(figsize=(6, 5))
            sns.heatmap(
                cm,
                annot=True,
                fmt="d",
                cmap="Blues",
                xticklabels=label_encoder.classes_,
                yticklabels=label_encoder.classes_,
            )
            plt.title(f"Confusion Matrix - {best_model_name}")
            plt.xlabel("Predicted")
            plt.ylabel("Actual")
            plt.tight_layout()
            plt.show()

            print(classification_report(y_test, best_predictions, target_names=label_encoder.classes_))
            """
        ),
        code_cell(
            """
            joblib.dump(scaler, ARTIFACTS_DIR / "scaler.pkl")
            joblib.dump(label_encoder, ARTIFACTS_DIR / "label_encoder.pkl")
            best_model.save(ARTIFACTS_DIR / "model_best.keras")

            with open(ARTIFACTS_DIR / "metrics_summary.json", "w", encoding="utf-8") as handle:
                json.dump(
                    {
                        "best_model": best_model_name,
                        "metrics": metrics_summary,
                        "feature_columns": FEATURE_COLUMNS,
                        "classes": label_encoder.classes_.tolist(),
                    },
                    handle,
                    indent=2,
                )

            print("Artifacts saved to:", ARTIFACTS_DIR)
            """
        ),
    ]

    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.11",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with NOTEBOOK_PATH.open("w", encoding="utf-8") as handle:
        json.dump(build_notebook(), handle, ensure_ascii=False, indent=2)
    print(f"Notebook scaffold written to {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
