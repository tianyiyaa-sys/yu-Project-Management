@echo off
setlocal
chcp 65001 >nul
title Yu PMO - Safe Update
cd /d "%~dp0"

echo ========================================
echo   Yu PMO - Safe Update
echo ========================================
echo.
echo The PMO page will start first.
echo Database/API problems will no longer block the UI.
echo.
pause

set "WORK=%TEMP%\yu-pmo-update"
set "ZIP=%TEMP%\yu-pmo-v1.zip"
set "SRC=%WORK%\yu-Project-Management-yu-pmo-v1"

echo.
echo [1/7] Cleaning temporary files...
if exist "%WORK%" rmdir /s /q "%WORK%"
if exist "%ZIP%" del /q "%ZIP%"
mkdir "%WORK%" >nul 2>&1

echo.
echo [2/7] Downloading latest PMO code...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/tianyiyaa-sys/yu-Project-Management/archive/refs/heads/yu-pmo-v1.zip' -OutFile '%ZIP%'"
if errorlevel 1 goto :download_error

echo.
echo [3/7] Extracting...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Expand-Archive -Path '%ZIP%' -DestinationPath '%WORK%' -Force"
if errorlevel 1 goto :extract_error

pushd "%SRC%"

echo.
echo [4/7] Building PMO UI...
docker compose -f docker-compose.yml -f docker-compose.yu-local.yml build pmo
if errorlevel 1 goto :ui_build_error

echo.
echo [5/7] Starting PMO UI first...
docker compose -f docker-compose.yml -f docker-compose.yu-local.yml up -d --no-deps pmo
if errorlevel 1 goto :ui_start_error

timeout /t 2 /nobreak >nul
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "try { $r=Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 'http://localhost:3100/'; if($r.StatusCode -ne 200){exit 1} } catch { exit 1 }"
if errorlevel 1 goto :ui_health_error

echo PMO UI is healthy.

echo.
echo [6/7] Building and starting PMO API/database...
docker compose -f docker-compose.yml -f docker-compose.yu-local.yml build pmo-api
if errorlevel 1 (
  echo WARNING: PMO API build failed. UI will remain available.
  goto :open_ui
)

docker compose -f docker-compose.yml -f docker-compose.yu-local.yml up -d pmo-db pmo-api
if errorlevel 1 (
  echo WARNING: PMO API/database startup failed. UI will remain available.
  goto :open_ui
)

timeout /t 3 /nobreak >nul
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "try { $r=Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 'http://localhost:3100/health'; if($r.StatusCode -ne 200){exit 1} } catch { exit 1 }"
if errorlevel 1 (
  echo WARNING: PMO API health check failed. UI is still available.
) else (
  echo PMO API and database are healthy.
)

:open_ui
echo.
echo [7/7] Opening PMO workbench...
start "" "http://localhost:3100"
echo.
echo PMO UI:  http://localhost:3100
echo Wekan:   http://localhost:3000
echo.
echo Service status:
docker compose -f docker-compose.yml -f docker-compose.yu-local.yml ps pmo pmo-api pmo-db
echo.
popd
pause
exit /b 0

:download_error
echo ERROR: Download failed.
goto :fatal
:extract_error
echo ERROR: Extract failed.
goto :fatal
:ui_build_error
echo ERROR: PMO UI build failed.
goto :fatal
:ui_start_error
echo ERROR: PMO UI startup failed.
goto :fatal
:ui_health_error
echo ERROR: PMO UI started but did not respond.
docker logs yu-pmo-app --tail 80
goto :fatal

:fatal
echo.
echo Please take a screenshot of this window and send it to ChatGPT.
echo.
if defined SRC (
  if exist "%SRC%" (
    pushd "%SRC%"
    docker compose -f docker-compose.yml -f docker-compose.yu-local.yml ps
    popd
  )
)
pause
exit /b 1
