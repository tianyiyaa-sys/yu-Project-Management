@echo off
setlocal
chcp 65001 >nul
title Yu Project Management - Update
cd /d "%~dp0"

echo ========================================
echo   Yu Project Management - Update
echo ========================================
echo.
echo This window will stay open so errors can be seen.
echo.
pause

echo.
echo [1/4] Checking Git...
where git
if errorlevel 1 (
  echo.
  echo ERROR: Git is not installed or not available in PATH.
  echo Please take a screenshot of this window and send it to ChatGPT.
  echo.
  pause
  exit /b 1
)

echo.
echo [2/4] Switching to yu-pmo-v1...
git fetch origin yu-pmo-v1
if errorlevel 1 (
  echo.
  echo ERROR: Cannot fetch latest code from GitHub.
  echo Please take a screenshot and send it to ChatGPT.
  echo.
  pause
  exit /b 1
)

git checkout yu-pmo-v1
if errorlevel 1 (
  echo.
  echo ERROR: Cannot switch to yu-pmo-v1.
  echo Please take a screenshot and send it to ChatGPT.
  echo.
  pause
  exit /b 1
)

git pull origin yu-pmo-v1
if errorlevel 1 (
  echo.
  echo ERROR: Cannot pull latest code.
  echo Please take a screenshot and send it to ChatGPT.
  echo.
  pause
  exit /b 1
)

echo.
echo [3/4] Rebuilding local app...
docker compose -f docker-compose.yml -f docker-compose.yu-local.yml up -d --build
if errorlevel 1 (
  echo.
  echo ERROR: Docker rebuild failed.
  echo Please take a screenshot and send it to ChatGPT.
  echo.
  pause
  exit /b 1
)

echo.
echo [4/4] Done. Opening browser...
timeout /t 8 /nobreak >nul
start "" "http://localhost:3000"

echo.
echo Update completed successfully.
echo.
pause
