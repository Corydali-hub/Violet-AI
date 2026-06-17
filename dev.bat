@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ====================================
echo   Violet-AI - Development Mode
echo ====================================
echo.

echo [1/2] Starting frontend dev server...
cd /d "%~dp0launcher\frontend"
start "Violet-AI Frontend" cmd /k "npm run dev"

echo [2/2] Starting backend dev server...
cd /d "%~dp0launcher"
start "Violet-AI Backend" cmd /k "python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000"

cd /d "%~dp0"
echo.
echo Servers started!
echo   Frontend : http://localhost:5173
echo   Backend  : http://localhost:8000
echo.
echo Press any key to close this window (servers will keep running)...
pause >nul
