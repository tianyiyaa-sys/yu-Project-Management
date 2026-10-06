@echo off
setlocal
title Yu Project Management - Local Start
cd /d "%~dp0"

echo ========================================
echo   Yu Project Management - Local Start
echo ========================================
echo.
echo This window will stay open so errors can be seen.
echo.
pause

echo.
echo [1/4] Checking Docker Desktop...
docker version
if errorlevel 1 (
  echo.
  echo ERROR: Docker Desktop is not running or docker command is unavailable.
  echo Please open Docker Desktop and wait until it is fully running.
  echo.
  pause
  exit /b 1
)

echo.
echo [2/4] Checking Docker Compose...
docker compose version
if errorlevel 1 (
  echo.
  echo ERROR: Docker Compose is unavailable.
  echo.
  pause
  exit /b 1
)

echo.
echo [3/4] Building and starting...
docker compose -f docker-compose.yml -f docker-compose.yu-local.yml up -d --build
if errorlevel 1 (
  echo.
  echo ERROR: Build or startup failed.
  echo Please take a screenshot of this window and send it to ChatGPT.
  echo.
  pause
  exit /b 1
)

echo.
echo [4/4] Opening browser...
timeout /t 10 /nobreak >nul
start "" "http://localhost:3000"

echo.
echo Started successfully.
echo If the page is not ready yet, wait 30-60 seconds and refresh.
echo.
pause
