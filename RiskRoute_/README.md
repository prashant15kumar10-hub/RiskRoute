# RiskRoute — Explainable Shipment Delay Prediction and Risk-Reduction System

**Constraint-Aware Explainable AI for Counterfactual Decision Optimization in Intelligent Logistics**

RiskRoute is a full-stack delivery decision-support system. A React
frontend communicates with a FastAPI backend, the ML engine predicts
delivery-delay risk, and SQLite stores users and simulation history.

## Main idea

Traditional model:

`shipment data → delay prediction`

RiskRoute:

`shipment data → delay prediction → constrained what-if search → feasible interventions`

Only three operational variables may change:

- vehicle load can decrease;
- departure can move earlier;
- schedule buffer can increase.

Distance, traffic, weather, driver experience, and shipment priority are treated as fixed context.

## Quick start

### One-click start

On Windows, double-click:

```text
START_PROJECT.bat
```

On macOS/Linux:

```bash
chmod +x START_PROJECT.sh
./START_PROJECT.sh
```

The launcher creates a Python virtual environment, installs Python and Node
dependencies, builds the React frontend, trains the model if it is missing,
and starts the FastAPI application at `http://localhost:8000`.

### Manual start

```bash
python -m venv .venv
```

Activate the environment, then:

```bash
pip install -r requirements.txt
python train.py
python evaluate_counterfactuals.py
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

On Windows, you may run `run.bat`. On Linux/macOS, run `bash run.sh`.

## Project structure

```text
riskroute/
├── backend/                       # FastAPI API, authentication and SQLite
├── frontend/                      # React and Vite interface
├── app.py                         # Legacy Streamlit interface
├── train.py                       # dataset generation + model training
├── evaluate_counterfactuals.py    # research evaluation
├── src/
│   ├── data.py                    # reproducible synthetic dataset
│   ├── model.py                   # preprocessing + classifier
│   └── counterfactual.py          # constrained search algorithm
├── tests/
├── data/
├── artifacts/
└── docs/
```

## Research contribution

The prototype tests whether explicit operational constraints improve actionability. Counterfactuals are evaluated using:

- validity: target risk is reached;
- constraint satisfaction: no forbidden feature changes;
- sparsity: number of changed features;
- proximity: normalized intervention cost;
- probability reduction;
- runtime.

## Important limitation

The included dataset is **synthetic and reproducible**, designed for methodology demonstration. It is not evidence that the model is production-ready. A publication submission should repeat the experiment on a real logistics dataset and report external validation.

## Suggested demo

1. Choose high traffic, high load, low buffer.
2. Show the predicted risk.
3. Set a target of 40%.
4. Open the first intervention.
5. Explain why immutable features remain unchanged.
6. Compare validity, sparsity, and runtime in `artifacts/counterfactual_summary.json`.
