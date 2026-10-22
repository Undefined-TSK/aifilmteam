@echo off
chcp 65001 >nul
title CINEAST React Workspace - Build

echo ============================================
echo   CINEAST React Workspace - Production Build
echo ============================================
echo.

cd /d D:\ai_film_projects\web\react-workspace

echo Checking dependencies...
if not exist "node_modules" (
    echo   Installing dependencies ^(first run^)...
    call npm install --ignore-scripts
    if errorlevel 1 (
        echo [ERROR] npm install failed.
        pause
        exit /b 1
    )
)

echo.
echo Building production bundle...
call npm run build
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed. Please check error messages above.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Build complete!
echo   Output: web\react-workspace\dist\
echo.
echo   Access via FastAPI:
echo   1. Run start_server.bat
echo   2. Open http://127.0.0.1:8190/workspace-react
echo      or http://127.0.0.1:8190/react/
echo ============================================
echo.
pause
