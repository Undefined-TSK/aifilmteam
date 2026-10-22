@echo off
title CINEAST ComfyUI
echo ============================================
echo   ComfyUI (SDXL Engine)
echo ============================================
echo.

REM Skip launch if already listening on 8188
netstat -ano | findstr ":8188.*LISTENING" >nul 2>&1
if %errorlevel%==0 (
  echo ComfyUI already running on port 8188, nothing to do.
  echo.
  pause
  exit /b 0
)

cd /d "D:\ai_film_projects\comfyui\ComfyUI_windows_portable"
echo Starting ComfyUI...
echo.
echo   URL:   http://127.0.0.1:8188
echo   Note:  Keep this window open while generating.
echo.
echo Press Ctrl+C to stop.
echo.
"python_embeded\python.exe" -s ComfyUI\main.py --windows-standalone-build --port 8188
pause
