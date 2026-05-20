@echo off
echo ========================================
echo   Correlation Heatmap Tool - Starting
echo ========================================
echo.

cd /d "%~dp0"

REM Create venv if not exists
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Install backend deps
echo Installing backend dependencies...
call venv\Scripts\activate.bat
pip install -r backend\requirements.txt -q

REM Install frontend deps
echo Installing frontend dependencies...
cd frontend
call npm install --silent
cd ..

REM Start backend
echo Starting backend on port 8000...
start "Heatmap-Backend" cmd /c "cd /d %~dp0 && call venv\Scripts\activate.bat && cd backend && python run.py"

REM Wait for backend
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting frontend on port 5173...
cd frontend
start "Heatmap-Frontend" cmd /c "npm run dev"

echo.
echo ========================================
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo ========================================
echo.
pause
