@echo off
REM run.bat - Windows script to run FIBOMed
REM Loads environment from secrets/.env and starts both backend and frontend servers

setlocal enabledelayedexpansion

echo ============================================
echo    FIBOMed - Medical Visual Storytelling
echo ============================================
echo.

REM Check if secrets/.env exists
if not exist "secrets\.env" (
    echo ERROR: secrets\.env file not found!
    echo Please create secrets\.env with required environment variables.
    echo See .env.example for reference.
    pause
    exit /b 1
)

echo [1/5] Loading environment variables from secrets/.env...
for /f "usebackq tokens=1,* delims==" %%a in ("secrets\.env") do (
    REM Skip empty lines and comments
    set "line=%%a"
    if defined line (
        if not "!line:~0,1!"=="#" (
            set "%%a=%%b"
        )
    )
)
echo       Environment variables loaded.
echo.

echo [2/5] Creating data directories...
if not exist "data\csv_files" mkdir "data\csv_files"
if not exist "data\generated\audio" mkdir "data\generated\audio"
if not exist "data\generated\prompts" mkdir "data\generated\prompts"
if not exist "data\generated\visualizations" mkdir "data\generated\visualizations"
if not exist "data\uploads\audio" mkdir "data\uploads\audio"
echo       Data directories ready.
echo.

echo [3/5] Checking Python virtual environment...
if not exist "backend\venv" (
    echo       Creating virtual environment...
    cd backend
    python -m venv venv
    cd ..
)
echo       Virtual environment ready.
echo.

echo [4/5] Starting Backend Server...
start "FIBOMed Backend" cmd /k "cd backend && venv\Scripts\activate && pip install -r requirements.txt -q && python main.py"
echo       Backend starting on http://localhost:8000
echo.

REM Wait for backend to initialize
echo       Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo [5/5] Starting Frontend Development Server...
start "FIBOMed Frontend" cmd /k "cd frontend && npm install && npm run dev"
echo       Frontend starting on http://localhost:5173
echo.

echo ============================================
echo    FIBOMed Services Started!
echo ============================================
echo.
echo    Backend API:  http://localhost:8000
echo    API Docs:     http://localhost:8000/docs
echo    Frontend:     http://localhost:5173
echo.
echo    To stop services, close the terminal windows
echo    or press Ctrl+C in each window.
echo ============================================
echo.

pause
