@echo off
setlocal
chcp 65001 >nul
title Yu PMO - Architecture Update
cd /d "%~dp0"

echo ========================================
echo   Yu PMO - Update
echo ========================================
echo.
echo This update rebuilds the PMO UI and PMO API.
echo Wekan stays running and will not be rebuilt.
echo.
pause

set "WORK=%TEMP%\yu-pmo-update"
set "ZIP=%TEMP%\yu-pmo-v1.zip"
set "SRC=%WORK%\yu-Project-Management-yu-pmo-v1"

echo.
echo [1/6] Cleaning temporary files...
if exist "%WORK%" rmdir /s /q "%WORK%"
if exist "%ZIP%" del /q "%ZIP%"
mkdir "%WORK%" >nul 2>&1

echo.
echo [2/6] Downloading latest PMO code...
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
echo [3/6] Extracting...
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
echo [4/6] Building PMO services...
pushd "%SRC%"
docker compose -f docker-compose.yml -f docker-compose.yu-local.yml build pmo-api pmo
if errorlevel 1 (
  echo.
  echo ERROR: PMO build failed.
  echo Please take a screenshot and send it to ChatGPT.
  echo.
  popd
  pause
  exit /b 1
)

echo.
echo [5/6] Starting PMO database, API and UI...
docker compose -f docker-compose.yml -f docker-compose.yu-local.yml up -d pmo-db pmo-api pmo
if errorlevel 1 (
  echo.
  echo ERROR: PMO startup failed.
  echo Please take a screenshot and send it to ChatGPT.
  echo.
  popd
  pause
  exit /b 1
)

echo.
echo [6/6] Done. Opening PMO workbench...
timeout /t 3 /nobreak >nul
start "" "http://localhost:3100"

echo.
echo PMO updated successfully.
echo PMO API and database are now running locally.
echo Wekan is still available at http://localhost:3000
echo.
popd
pause
