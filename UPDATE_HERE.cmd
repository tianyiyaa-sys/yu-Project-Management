@echo off
setlocal
chcp 65001 >nul
title Yu Project Management - Update
cd /d "%~dp0"

echo ========================================
echo   Yu Project Management - Update
echo ========================================
echo.
echo No Git knowledge is required.
echo This updater downloads the latest yu-pmo-v1 ZIP automatically.
echo.
pause

set "WORK=%TEMP%\yu-pmo-update"
set "ZIP=%TEMP%\yu-pmo-v1.zip"
set "SRC=%WORK%\yu-Project-Management-yu-pmo-v1"

echo.
echo [1/5] Cleaning temporary files...
if exist "%WORK%" rmdir /s /q "%WORK%"
if exist "%ZIP%" del /q "%ZIP%"
mkdir "%WORK%" >nul 2>&1

echo.
echo [2/5] Downloading latest code from GitHub...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/tianyiyaa-sys/yu-Project-Management/archive/refs/heads/yu-pmo-v1.zip' -OutFile '%ZIP%'"
if errorlevel 1 (
  echo.
  echo ERROR: Download failed.
  echo Please take a screenshot and send it to ChatGPT.
  echo.
  pause
  exit /b 1
)

echo.
echo [3/5] Extracting...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Expand-Archive -Path '%ZIP%' -DestinationPath '%WORK%' -Force"
if errorlevel 1 (
  echo.
  echo ERROR: Extract failed.
  echo Please take a screenshot and send it to ChatGPT.
  echo.
  pause
  exit /b 1
)

echo.
echo [4/5] Rebuilding latest version...
pushd "%SRC%"
docker compose -f docker-compose.yml -f docker-compose.yu-local.yml up -d --build
if errorlevel 1 (
  echo.
  echo ERROR: Docker rebuild failed.
  echo Please take a screenshot and send it to ChatGPT.
  echo.
  popd
  pause
  exit /b 1
)

echo.
echo [5/5] Update complete.
timeout /t 8 /nobreak >nul
start "" "http://localhost:3000"

echo.
echo The newest version is running.
echo Your Docker data is kept in the same local volume.
echo.
popd
pause
