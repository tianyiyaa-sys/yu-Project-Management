@echo off
setlocal
chcp 65001 >nul
title Yu Project Management - Local Start
cd /d "%~dp0"

echo ========================================
echo   Yu Project Management - Local Start
echo ========================================
echo.
echo This starts both Wekan and the Yu PMO workbench.
echo.
pause

echo.
echo [1/4] Checking Docker Desktop...
docker version >nul 2>&1
if errorlevel 1 (
  echo.
  echo ERROR: Docker Desktop is not running.
  echo Please open Docker Desktop first.
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
echo [3/4] Starting local services...
docker compose -f docker-compose.yml -f docker-compose.yu-local.yml up -d
if errorlevel 1 (
  echo.
  echo ERROR: Startup failed.
  echo Please take a screenshot and send it to ChatGPT.
  echo.
  pause
  exit /b 1
)

echo.
echo [4/4] Opening Yu PMO workbench...
timeout /t 3 /nobreak >nul
start "" "http://localhost:3100"

echo.
echo Started successfully.
echo PMO:   http://localhost:3100
echo Wekan: http://localhost:3000
echo.
pause
