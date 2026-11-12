from __future__ import annotations

import json
import time
from pathlib import Path

import pandas as pd
import numpy as np

from src.counterfactual import generate_counterfactuals, verify_constraints
from src.data import FEATURES
from src.model import load_model


ROOT = Path(__file__).resolve().parent


def main() -> None:
    model = load_model(str(ROOT / "artifacts" / "delay_model.joblib"))
    test = pd.read_csv(ROOT / "artifacts" / "test_predictions.csv")
    high_risk = test[test["predicted_probability"] >= 0.60].head(150)
    low_risk_pool = test[test["predicted_probability"] <= 0.40].copy()
    feature_ranges = test[FEATURES].max() - test[FEATURES].min()
    feature_ranges = feature_ranges.replace(0, 1)
    rows = []
    baseline_rows = []
    start = time.perf_counter()
    for _, row in high_risk.iterrows():
        record = {name: float(row[name]) for name in FEATURES}
        results = generate_counterfactuals(model, record)
        best = results[0] if results else None
        rows.append(
            {
                "initial_probability": row["predicted_probability"],
                "found": bool(best),
                "final_probability": best["delay_probability"] if best else None,
                "action_count": len(best["changes"]) if best else None,
                "normalized_cost": best["cost"] if best else None,
                "constraints_valid": verify_constraints(record, best) if best else None,
            }
        )

        # Baseline: nearest observed low-risk case across every feature.
        # It reaches the target but ignores which attributes are actionable.
        distances = (
            (low_risk_pool[FEATURES] - pd.Series(record)).abs() / feature_ranges
        ).sum(axis=1)
        nearest = low_risk_pool.loc[distances.idxmin()]
        immutable = [name for name in FEATURES if name not in {
            "vehicle_load_pct", "departure_hour", "buffer_minutes"
        }]
        baseline_rows.append(
            {
                "target_valid": bool(nearest["predicted_probability"] <= 0.40),
                "constraints_valid": bool(
                    np.allclose(
                        nearest[immutable].astype(float).to_numpy(),
                        np.array([record[name] for name in immutable], dtype=float),
                    )
                ),
                "changed_features": int(
                    sum(float(nearest[name]) != float(record[name]) for name in FEATURES)
                ),
            }
        )
    elapsed = time.perf_counter() - start
    result = pd.DataFrame(rows)
    baseline = pd.DataFrame(baseline_rows)
    result.to_csv(ROOT / "artifacts" / "counterfactual_results.csv", index=False)
    baseline.to_csv(ROOT / "artifacts" / "baseline_results.csv", index=False)
    summary = {
        "evaluated_high_risk_cases": int(len(result)),
        "validity_rate": round(float(result["found"].mean()), 4),
        "constraint_satisfaction_rate": round(
            float(result.loc[result["found"], "constraints_valid"].mean()), 4
        ),
        "mean_action_count": round(float(result["action_count"].mean()), 3),
        "mean_normalized_cost": round(float(result["normalized_cost"].mean()), 3),
        "mean_probability_reduction": round(
            float((result["initial_probability"] - result["final_probability"]).mean()), 4
        ),
        "mean_runtime_ms": round(1000 * elapsed / max(len(result), 1), 3),
        "nearest_case_baseline": {
            "validity_rate": round(float(baseline["target_valid"].mean()), 4),
            "constraint_satisfaction_rate": round(
                float(baseline["constraints_valid"].mean()), 4
            ),
            "mean_changed_features": round(
                float(baseline["changed_features"].mean()), 3
            ),
        },
    }
    (ROOT / "artifacts" / "counterfactual_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
