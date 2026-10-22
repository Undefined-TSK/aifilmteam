@echo off
title CINEAST Server
echo ============================================
echo   CINEAST Server (FastAPI)
echo ============================================
echo.

REM Kill any existing process on port 8190
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8190.*LISTENING"') do (
  echo Killing old process PID %%a ...
  taskkill /F /PID %%a 2>nul
)

echo Starting server...
echo.
echo   Showcase:  http://127.0.0.1:8190/
echo   Workspace: http://127.0.0.1:8190/workspace
echo   API Docs:  http://127.0.0.1:8190/docs
echo.
echo Press Ctrl+C to stop.
echo.
python "D:\ai_film_projects\tools\api_server.py"
pause
