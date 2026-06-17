@echo off
chcp 65001 >nul
echo ====================================
echo  堇言AI - 开发调试模式
echo ====================================
echo.

echo [1/2] 启动前端开发服务器 (npm run dev)...
start "堇言AI-前端" cmd /k "cd frontend && npm run dev"

echo [2/2] 启动后端开发服务器 (uvicorn --reload)...
start "堇言AI-后端" cmd /k "uvicorn app:app --reload --host 0.0.0.0 --port 8000"

echo.
echo ✅ 开发服务器已启动！
echo 📌 前端地址: http://localhost:5173
echo 📌 后端地址: http://localhost:8000
echo.
echo 按任意键关闭此窗口（不会关闭已启动的服务）...
pause >nul