@echo off
chcp 65001 >nul

echo ========================================
echo   Bilibili Highlight Clip Tool
echo ========================================
echo.

echo [1/2] Starting backend (port 8001)...
cd /d "%~dp0backend"
start "Backend" cmd /k "chcp 65001 >nul && python run.py"

echo [2/2] Starting frontend (port 5174)...
cd /d "%~dp0frontend"
start "Frontend" cmd /k "chcp 65001 >nul && npm run dev"

echo.
echo Done!
echo   Frontend: http://localhost:5174
echo   Backend:  http://localhost:8001
echo.
pause
