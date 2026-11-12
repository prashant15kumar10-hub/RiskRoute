from __future__ import annotations

import numpy as np
import pandas as pd


FEATURES = [
    "distance_km",
    "vehicle_load_pct",
    "departure_hour",
    "traffic_level",
    "weather_severity",
    "driver_experience_years",
    "priority_shipment",
    "buffer_minutes",
]


def generate_logistics_data(n_rows: int = 6000, seed: int = 42) -> pd.DataFrame:
    """Generate a reproducible teaching dataset with realistic feature interactions."""
    rng = np.random.default_rng(seed)
    distance = rng.uniform(20, 800, n_rows)
    load = np.clip(rng.normal(73, 17, n_rows), 25, 100)
    departure = rng.integers(0, 24, n_rows)
    rush = ((departure >= 7) & (departure <= 10)) | ((departure >= 17) & (departure <= 20))
    traffic = np.clip(rng.poisson(1.1 + 1.15 * rush), 0, 3)
    weather = rng.choice([0, 1, 2, 3], n_rows, p=[0.48, 0.30, 0.16, 0.06])
    experience = np.clip(rng.gamma(2.2, 2.0, n_rows), 0, 18)
    priority = rng.binomial(1, 0.27, n_rows)
    buffer = np.clip(rng.normal(35 + 18 * priority, 20, n_rows), 0, 120)

    score = (
        -3.25
        + 0.0027 * distance
        + 0.030 * (load - 60)
        + 0.62 * traffic
        + 0.53 * weather
        - 0.075 * experience
        - 0.019 * buffer
        + 0.48 * rush
        - 0.20 * priority
        + 0.0009 * distance * traffic
        + rng.normal(0, 0.65, n_rows)
    )
    probability = 1 / (1 + np.exp(-score))
    delayed = rng.binomial(1, probability)

    return pd.DataFrame(
        {
            "distance_km": distance.round(1),
            "vehicle_load_pct": load.round(1),
            "departure_hour": departure,
            "traffic_level": traffic,
            "weather_severity": weather,
            "driver_experience_years": experience.round(1),
            "priority_shipment": priority,
            "buffer_minutes": buffer.round(0),
            "delayed": delayed,
        }
    )


def save_dataset(path: str, n_rows: int = 6000, seed: int = 42) -> pd.DataFrame:
    df = generate_logistics_data(n_rows=n_rows, seed=seed)
    df.to_csv(path, index=False)
    return df
