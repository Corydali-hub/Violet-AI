@echo off
chcp 65001 >nul

:: Anchor to script directory (run from anywhere)
cd /d "%~dp0"

echo ====================================
echo   Violet-AI - Production Mode
echo ====================================
echo.

:: Check frontend build
if not exist "launcher\static\index.html" (
    echo [WARN] Frontend build not found (launcher\static\index.html)
    echo Building frontend...
    cd /d "%~dp0launcher\frontend"
    if errorlevel 1 (
        echo [ERROR] Cannot enter frontend directory.
        pause
        exit /b
    )
    call npm run build
    if errorlevel 1 (
        echo [ERROR] Frontend build failed.
        pause
        exit /b
    )
    cd /d "%~dp0"
    echo [ OK ] Frontend build complete!
)

echo [ OK ] Starting backend server...
cd /d "%~dp0launcher"
start http://localhost:8000
uvicorn app:app --host 0.0.0.0 --port 8000
