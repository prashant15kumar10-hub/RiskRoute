from pathlib import Path

import streamlit as st

from src.counterfactual import delay_probability, generate_counterfactuals
from src.model import load_model


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "artifacts" / "delay_model.joblib"

st.set_page_config(page_title="RiskRoute", page_icon="🚚", layout="wide")
st.title("RiskRoute")
st.caption("Constraint-aware what-if simulation for delivery-delay decisions")

if not MODEL_PATH.exists():
    st.error("Model not found. Run `python train.py` first.")
    st.stop()

model = load_model(str(MODEL_PATH))

with st.sidebar:
    st.header("Shipment conditions")
    distance = st.slider("Distance (km)", 20, 800, 420)
    load = st.slider("Vehicle load (%)", 25, 100, 90)
    departure = st.slider("Departure hour", 0, 23, 10)
    traffic = st.select_slider("Traffic level", options=[0, 1, 2, 3], value=3)
    weather = st.select_slider("Weather severity", options=[0, 1, 2, 3], value=1)
    experience = st.slider("Driver experience (years)", 0, 18, 4)
    priority = st.checkbox("Priority shipment", value=False)
    buffer = st.slider("Schedule buffer (minutes)", 0, 120, 20, step=5)
    target = st.slider("Target maximum delay risk", 0.15, 0.50, 0.40, step=0.05)

record = {
    "distance_km": distance,
    "vehicle_load_pct": load,
    "departure_hour": departure,
    "traffic_level": traffic,
    "weather_severity": weather,
    "driver_experience_years": experience,
    "priority_shipment": int(priority),
    "buffer_minutes": buffer,
}

probability = delay_probability(model, record)
left, right = st.columns([1, 2])
with left:
    st.metric("Predicted delay risk", f"{probability:.1%}")
    st.progress(probability)
    st.write("Risk label:", "**High**" if probability >= 0.60 else "**Moderate**" if probability >= 0.40 else "**Low**")

with right:
    st.subheader("Decision context")
    st.write(
        "The model uses operational and environmental conditions. "
        "The counterfactual engine may change only load, departure time, and buffer."
    )
    st.info("Distance, weather, traffic, driver experience, and priority status remain fixed.")

st.divider()
st.subheader("Recommended feasible interventions")
results = generate_counterfactuals(model, record, target_probability=target)
if not results:
    st.warning("No feasible intervention in the current search limits reaches the selected target.")
else:
    for index, result in enumerate(results, start=1):
        with st.expander(
            f"Scenario {index}: risk {result['delay_probability']:.1%} "
            f"({probability - result['delay_probability']:.1%} reduction)",
            expanded=index == 1,
        ):
            columns = st.columns(max(len(result["changes"]), 1))
            for column, (name, change) in zip(columns, result["changes"].items()):
                column.metric(name.replace("_", " ").title(), change["to"], delta=change["to"] - change["from"])
            st.caption(f"Normalized intervention cost: {result['cost']:.2f}")

st.divider()
st.caption(
    "Educational prototype. Predictions and recommendations must be validated with real operational data "
    "before production use."
)
