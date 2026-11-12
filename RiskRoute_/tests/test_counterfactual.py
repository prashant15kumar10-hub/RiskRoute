from pathlib import Path

import pandas as pd

from src.counterfactual import generate_counterfactuals, verify_constraints
from src.data import FEATURES
from src.model import load_model


ROOT = Path(__file__).resolve().parents[1]


def test_counterfactual_constraints():
    model = load_model(str(ROOT / "artifacts" / "delay_model.joblib"))
    test = pd.read_csv(ROOT / "artifacts" / "test_predictions.csv")
    results = []
    record = None
    for _, row in test[test["predicted_probability"] >= 0.60].iterrows():
        candidate = {name: float(row[name]) for name in FEATURES}
        found = generate_counterfactuals(model, candidate, target_probability=0.45)
        if found:
            record, results = candidate, found
            break
    assert results
    assert record is not None
    assert all(verify_constraints(record, result) for result in results)
    assert all(result["delay_probability"] <= 0.45 for result in results)
