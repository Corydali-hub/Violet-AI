@echo off
chcp 65001 >nul

:: Anchor to script directory (run from anywhere)
cd /d "%~dp0"

echo ====================================
echo   Violet-AI - Development Mode
echo ====================================
echo.

echo [1/2] Starting frontend dev server (npm run dev)...
start "Violet-AI Frontend" cmd /k "cd /d \"%~dp0launcher\frontend\" && npm run dev"

echo [2/2] Starting backend dev server (uvicorn --reload)...
start "Violet-AI Backend" cmd /k "cd /d \"%~dp0launcher\" && uvicorn app:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Servers started!
echo   Frontend : http://localhost:5173
echo   Backend  : http://localhost:8000
echo.
echo Press any key to close this window (servers will keep running)...
pause >nul
