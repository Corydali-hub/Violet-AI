@echo off
chcp 65001 >nul
echo ====================================
echo  堇言AI - 生产使用模式
echo ====================================
echo.

:: 检查前端构建产物
if not exist "static\index.html" (
    echo ❌ 未找到前端构建产物 (static\index.html)
    echo 正在自动构建前端...
    cd /d "%~dp0frontend" || exit /b
    call npm run build
    if errorlevel 1 (
        echo ❌ 前端构建失败，请手动检查。
        pause
        exit /b
    )
    cd /d "%~dp0"
    echo ✅ 前端构建完成！
)

echo ✅ 前端已构建，启动后端服务...
:: 启动后端并在浏览器中打开
start http://localhost:8000
uvicorn app:app --host 0.0.0.0 --port 8000