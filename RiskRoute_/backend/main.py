from __future__ import annotations

import math
from pathlib import Path
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field

from backend.database import (
    authenticate,
    create_user,
    initialize,
    prediction_history,
    save_prediction,
    user_for_token,
)
from src.counterfactual import delay_probability, generate_counterfactuals
from src.model import load_model


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "artifacts" / "delay_model.joblib"
FRONTEND_DIST = ROOT / "frontend" / "dist"

app = FastAPI(title="RiskRoute API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

initialize()
model = load_model(str(MODEL_PATH)) if MODEL_PATH.exists() else None


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)


class Registration(Credentials):
    name: str = Field(min_length=2, max_length=60)


class Shipment(BaseModel):
    distance_km: float = Field(ge=20, le=800)
    vehicle_load_pct: float = Field(ge=25, le=100)
    departure_hour: int = Field(ge=0, le=23)
    traffic_level: int = Field(ge=0, le=3)
    weather_severity: int = Field(ge=0, le=3)
    driver_experience_years: float = Field(ge=0, le=18)
    priority_shipment: int = Field(ge=0, le=1)
    buffer_minutes: float = Field(ge=0, le=120)
    target_probability: float = Field(default=0.40, ge=0.15, le=0.50)


class RiskProfileRequest(Shipment):
    factor: Literal["vehicle_load_pct", "buffer_minutes", "departure_hour"] = (
        "vehicle_load_pct"
    )


class SafetyCheck(BaseModel):
    product_sealed: bool = True
    product_labeled: bool = True
    temperature_controlled: bool = True
    hazardous_documentation: bool = True
    load_secured: bool = True
    tire_condition: int = Field(default=90, ge=0, le=100)
    brake_condition: int = Field(default=90, ge=0, le=100)
    fuel_level: int = Field(default=75, ge=0, le=100)
    maintenance_overdue: bool = False
    driver_rest_hours: float = Field(default=8, ge=0, le=24)


def current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Sign in is required.")
    token = authorization.split(" ", 1)[1]
    user = user_for_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired. Sign in again.")
    return user


@app.get("/api/health")
def health():
    return {"status": "ok", "model_ready": model is not None}


@app.post("/api/register")
def register(payload: Registration):
    try:
        return create_user(payload.name, payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/api/login")
def login(payload: Credentials):
    try:
        return authenticate(payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@app.post("/api/predict")
def predict(payload: Shipment, user: dict = Depends(current_user)):
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not trained.")
    record = payload.model_dump(exclude={"target_probability"})
    probability = delay_probability(model, record)
    raw = generate_counterfactuals(
        model, record, target_probability=payload.target_probability, max_results=5
    )
    scenarios = [
        {
            "delay_probability": round(item["delay_probability"], 5),
            "cost": round(item["cost"], 4),
            "changes": item["changes"],
        }
        for item in raw
    ]
    prediction_id = save_prediction(user["id"], record, probability, scenarios)
    return {
        "id": prediction_id,
        "delay_probability": round(probability, 5),
        "risk_label": "High" if probability >= 0.60 else "Moderate" if probability >= 0.40 else "Low",
        "target_probability": payload.target_probability,
        "scenarios": scenarios,
    }


@app.get("/api/history")
def history(user: dict = Depends(current_user)):
    return prediction_history(user["id"])


@app.post("/api/risk-profile")
def risk_profile(payload: RiskProfileRequest, _: dict = Depends(current_user)):
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not trained.")
    record = payload.model_dump(exclude={"target_probability", "factor"})
    values = {
        "vehicle_load_pct": [30, 40, 50, 60, 70, 80, 90, 100],
        "buffer_minutes": [0, 15, 30, 45, 60, 75, 90, 105, 120],
        "departure_hour": [0, 3, 6, 9, 12, 15, 18, 21, 23],
    }[payload.factor]
    points = []
    for value in values:
        candidate = dict(record)
        candidate[payload.factor] = value
        points.append(
            {"value": value, "risk": round(delay_probability(model, candidate), 5)}
        )
    return {
        "factor": payload.factor,
        "current_value": record[payload.factor],
        "current_risk": round(delay_probability(model, record), 5),
        "points": points,
    }


@app.post("/api/verify-safety")
def verify_safety(payload: SafetyCheck, _: dict = Depends(current_user)):
    product_checks = [
        ("Packaging sealed", payload.product_sealed, 30),
        ("Safety label attached", payload.product_labeled, 25),
        ("Temperature requirement met", payload.temperature_controlled, 25),
        ("Hazard documents complete", payload.hazardous_documentation, 20),
    ]
    vehicle_checks = [
        ("Cargo secured", payload.load_secured, 20),
        ("Tires at or above 70%", payload.tire_condition >= 70, 20),
        ("Brakes at or above 70%", payload.brake_condition >= 70, 25),
        ("Fuel at or above 25%", payload.fuel_level >= 25, 10),
        ("Maintenance current", not payload.maintenance_overdue, 15),
        ("Driver rested at least 7h", payload.driver_rest_hours >= 7, 10),
    ]
    product_score = sum(weight for _, passed, weight in product_checks if passed)
    vehicle_score = sum(weight for _, passed, weight in vehicle_checks if passed)
    blockers = [
        label
        for label, passed, _ in product_checks + vehicle_checks
        if not passed
    ]
    return {
        "product_score": product_score,
        "vehicle_score": vehicle_score,
        "overall_score": round((product_score + vehicle_score) / 2),
        "safe_to_dispatch": not blockers,
        "product_checks": [
            {"label": label, "passed": passed} for label, passed, _ in product_checks
        ],
        "vehicle_checks": [
            {"label": label, "passed": passed} for label, passed, _ in vehicle_checks
        ],
        "blockers": blockers,
        "notice": "Prototype screening only; not a certified safety inspection.",
    }


@app.post("/api/rank-drivers")
def rank_drivers(payload: Shipment, _: dict = Depends(current_user)):
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not trained.")
    drivers = [
        {"name": "Aarav Sharma", "experience": 8.5, "incidents": 0, "rest_hours": 8.5, "skills": ["Defensive driving", "Cargo securing", "Eco driving"]},
        {"name": "Meera Singh", "experience": 6.0, "incidents": 0, "rest_hours": 7.5, "skills": ["Defensive driving", "Adverse-weather driving"]},
        {"name": "Rohan Verma", "experience": 4.0, "incidents": 1, "rest_hours": 8.0, "skills": ["Cargo securing", "Route planning"]},
        {"name": "Ishita Patel", "experience": 3.0, "incidents": 0, "rest_hours": 6.0, "skills": ["Eco driving", "Route planning"]},
        {"name": "Kabir Rao", "experience": 2.0, "incidents": 2, "rest_hours": 7.0, "skills": ["Basic cargo handling"]},
    ]
    base = payload.model_dump(exclude={"target_probability"})
    ranked = []
    for driver in drivers:
        record = dict(base)
        record["driver_experience_years"] = driver["experience"]
        risk = delay_probability(model, record)
        skill_lower = " ".join(driver["skills"]).lower()
        if "defensive" in skill_lower:
            risk -= 0.05
        if "cargo securing" in skill_lower:
            risk -= 0.035
        if "route planning" in skill_lower:
            risk -= 0.02
        risk += driver["incidents"] * 0.035
        if driver["rest_hours"] < 7:
            risk += 0.08
        risk = min(0.99, max(0.01, risk))
        if driver["rest_hours"] < 7:
            recommendation = "Fatigue management"
        elif payload.weather_severity >= 2 and "adverse-weather" not in skill_lower:
            recommendation = "Adverse-weather driving"
        elif payload.traffic_level >= 2 and "defensive" not in skill_lower:
            recommendation = "Defensive driving"
        elif payload.vehicle_load_pct >= 75 and "cargo securing" not in skill_lower:
            recommendation = "Advanced cargo securing"
        else:
            recommendation = "Maintain current safety practice"
        ranked.append(
            {
                **driver,
                "risk": round(risk, 5),
                "safe_arrival_likelihood": round(1 - risk, 5),
                "recommended_skill": recommendation,
            }
        )
    ranked.sort(key=lambda item: (item["risk"], -item["experience"]))
    for position, driver in enumerate(ranked, start=1):
        driver["rank"] = position
    return {
        "drivers": ranked,
        "notice": "Educational risk ranking, not an employment decision.",
    }


if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{path:path}")
    def frontend(path: str):
        requested = FRONTEND_DIST / path
        if path and requested.is_file():
            return FileResponse(requested)
        return FileResponse(FRONTEND_DIST / "index.html")
