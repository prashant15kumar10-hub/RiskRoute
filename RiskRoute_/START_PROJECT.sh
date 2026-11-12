#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "=========================================="
echo "      Starting RiskRoute"
echo "=========================================="

PYTHON=python3
command -v "$PYTHON" >/dev/null 2>&1 || {
  echo "Python 3 was not found. Install Python 3.10 or newer."
  exit 1
}
command -v npm >/dev/null 2>&1 || {
  echo "Node.js was not found. Install the Node.js LTS version from https://nodejs.org/"
  exit 1
}

if [ ! -x ".venv/bin/python" ]; then
  echo "[1/5] Creating virtual environment..."
  "$PYTHON" -m venv .venv
else
  echo "[1/5] Virtual environment already exists."
fi

echo "[2/5] Installing Python packages..."
".venv/bin/python" -m pip install --upgrade pip
".venv/bin/python" -m pip install -r requirements.txt

if [ ! -f "artifacts/delay_model.joblib" ]; then
  echo "[3/5] Training the model..."
  ".venv/bin/python" train.py
else
  echo "[3/5] Trained model already exists."
fi

echo "[4/5] Building the React frontend..."
(cd frontend && npm install && npm run build)

echo "[5/5] Opening RiskRoute Full-Stack..."
echo "The application will open at http://localhost:8000"
if command -v xdg-open >/dev/null 2>&1; then xdg-open http://localhost:8000 >/dev/null 2>&1 || true; fi
if command -v open >/dev/null 2>&1; then open http://localhost:8000 >/dev/null 2>&1 || true; fi
".venv/bin/python" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
