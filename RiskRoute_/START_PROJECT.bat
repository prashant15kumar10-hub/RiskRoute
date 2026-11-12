@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo       Starting RiskRoute
echo ==========================================

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found.
    echo Install Python 3.10 or newer and select "Add Python to PATH".
    pause
    exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
    echo Node.js was not found.
    echo Install the Node.js LTS version from https://nodejs.org/
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [1/5] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 goto :error
) else (
    echo [1/5] Virtual environment already exists.
)

echo [2/5] Installing Python packages...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

if not exist "artifacts\delay_model.joblib" (
    echo [3/5] Training the model...
    ".venv\Scripts\python.exe" train.py
    if errorlevel 1 goto :error
) else (
    echo [3/5] Trained model already exists.
)

echo [4/5] Building the React frontend...
pushd frontend
call npm install
if errorlevel 1 goto :error
call npm run build
if errorlevel 1 goto :error
popd

echo [5/5] Opening RiskRoute Full-Stack...
echo The application will open at http://localhost:8000
start "" http://localhost:8000
".venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
exit /b 0

:error
echo.
echo Setup failed. Read the error above, then try again.
pause
exit /b 1
