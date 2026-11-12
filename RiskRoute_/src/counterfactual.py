from __future__ import annotations

from itertools import product
from typing import Any

import pandas as pd

from .data import FEATURES


ACTION_RULES = {
    "vehicle_load_pct": [0, -5, -10, -15, -20],
    "departure_hour": [0, -1, -2, -3],
    "buffer_minutes": [0, 15, 30, 45, 60],
}


def delay_probability(model: Any, record: dict) -> float:
    row = pd.DataFrame([{name: record[name] for name in FEATURES}])
    return float(model.predict_proba(row)[0, 1])


def _normalized_cost(original: dict, candidate: dict) -> float:
    return (
        abs(candidate["vehicle_load_pct"] - original["vehicle_load_pct"]) / 25
        + abs(candidate["departure_hour"] - original["departure_hour"]) / 4
        + abs(candidate["buffer_minutes"] - original["buffer_minutes"]) / 60
    )


def generate_counterfactuals(
    model: Any,
    record: dict,
    target_probability: float = 0.40,
    max_results: int = 5,
) -> list[dict]:
    """Enumerate feasible operational changes and return minimal valid actions.

    Immutable context (distance, traffic, weather, driver experience and priority)
    is preserved. Mutable actions are constrained to realistic directions.
    """
    candidates = []
    for load_delta, hour_delta, buffer_delta in product(
        ACTION_RULES["vehicle_load_pct"],
        ACTION_RULES["departure_hour"],
        ACTION_RULES["buffer_minutes"],
    ):
        candidate = dict(record)
        candidate["vehicle_load_pct"] = max(25, record["vehicle_load_pct"] + load_delta)
        candidate["departure_hour"] = max(0, record["departure_hour"] + hour_delta)
        candidate["buffer_minutes"] = min(120, record["buffer_minutes"] + buffer_delta)

        if candidate == record:
            continue
        probability = delay_probability(model, candidate)
        if probability <= target_probability:
            changed = {
                key: {"from": record[key], "to": candidate[key]}
                for key in ACTION_RULES
                if candidate[key] != record[key]
            }
            candidates.append(
                {
                    "delay_probability": probability,
                    "cost": _normalized_cost(record, candidate),
                    "changes": changed,
                    "record": candidate,
                }
            )

    candidates.sort(key=lambda item: (item["cost"], item["delay_probability"], len(item["changes"])))
    diverse = []
    signatures = set()
    for item in candidates:
        signature = tuple(item["changes"].keys())
        if signature not in signatures or len(diverse) < 2:
            signatures.add(signature)
            diverse.append(item)
        if len(diverse) == max_results:
            break
    return diverse


def verify_constraints(original: dict, result: dict) -> bool:
    candidate = result["record"]
    immutable = [name for name in FEATURES if name not in ACTION_RULES]
    return (
        all(candidate[name] == original[name] for name in immutable)
        and candidate["vehicle_load_pct"] <= original["vehicle_load_pct"]
        and candidate["departure_hour"] <= original["departure_hour"]
        and candidate["buffer_minutes"] >= original["buffer_minutes"]
    )
