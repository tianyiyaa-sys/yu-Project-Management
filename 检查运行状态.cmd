@echo off
setlocal
chcp 65001 >nul
title Yu Project Management - Status Check
cd /d "%~dp0"

echo ========================================
echo   Yu Project Management - Status Check
echo ========================================
echo.
echo [1] Container status
echo ----------------------------------------
docker compose -f docker-compose.yml -f docker-compose.yu-local.yml ps -a

echo.
echo [2] Wekan logs
echo ----------------------------------------
docker logs --tail 120 wekan-app 2>&1

echo.
echo [3] Database logs
echo ----------------------------------------
docker logs --tail 120 wekan-ferretdb 2>&1

echo.
echo ========================================
echo Please take a screenshot of this window
echo and send it to ChatGPT.
echo ========================================
echo.
pause
