@echo off
chcp 65001 >nul
title CINEAST React Workspace (Dev Server)

echo ============================================
echo   CINEAST React Workspace - Dev Server
echo ============================================
echo.

cd /d D:\ai_film_projects\web\react-workspace

echo [1/3] Checking dependencies...
if not exist "node_modules" (
    echo   Installing npm packages ^(first run, may take a minute^)...
    call npm install
    if errorlevel 1 (
        echo.
        echo [ERROR] npm install failed. Please check your Node.js installation.
        pause
        exit /b 1
    )
    echo   Dependencies installed.
) else (
    echo   Dependencies found.
)
echo.

echo [2/3] Starting FastAPI backend ^(port 8190^)...
start "CINEAST API Server" cmd /c "cd /d D:\ai_film_projects && start_server.bat"
timeout /t 3 /nobreak >nul
echo   Backend started.
echo.

echo [3/3] Starting Vite dev server ^(port 5173^)...
echo.
echo ============================================
echo   Workspace:  http://localhost:5173/react/
echo   API:        http://127.0.0.1:8190
echo   API docs:   http://127.0.0.1:8190/docs
echo ============================================
echo.
echo Press Ctrl+C to stop both servers.
echo.

call npm run dev
