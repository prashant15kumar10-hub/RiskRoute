from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .data import FEATURES

CATEGORICAL = ["traffic_level", "weather_severity", "priority_shipment"]
NUMERICAL = [name for name in FEATURES if name not in CATEGORICAL]


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        [
            ("num", StandardScaler(), NUMERICAL),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL),
        ]
    )
    classifier = HistGradientBoostingClassifier(
        learning_rate=0.08,
        max_iter=180,
        max_leaf_nodes=21,
        l2_regularization=0.4,
        random_state=42,
    )
    return Pipeline([("preprocess", preprocessor), ("model", classifier)])


def train_and_evaluate(
    csv_path: str,
    model_path: str,
    metrics_path: str,
    test_predictions_path: str,
) -> dict:
    df = pd.read_csv(csv_path)
    x_train, x_test, y_train, y_test = train_test_split(
        df[FEATURES],
        df["delayed"],
        test_size=0.25,
        stratify=df["delayed"],
        random_state=42,
    )
    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)
    probability = pipeline.predict_proba(x_test)[:, 1]
    prediction = (probability >= 0.5).astype(int)
    metrics = {
        "rows": int(len(df)),
        "test_rows": int(len(x_test)),
        "positive_rate": round(float(df["delayed"].mean()), 4),
        "accuracy": round(float(accuracy_score(y_test, prediction)), 4),
        "precision": round(float(precision_score(y_test, prediction)), 4),
        "recall": round(float(recall_score(y_test, prediction)), 4),
        "f1": round(float(f1_score(y_test, prediction)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, probability)), 4),
    }
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)
    Path(metrics_path).write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    output = x_test.copy()
    output["actual"] = y_test.to_numpy()
    output["predicted_probability"] = probability.round(5)
    output["predicted_class"] = prediction
    output.to_csv(test_predictions_path, index=False)
    return metrics


def load_model(path: str):
    return joblib.load(path)
