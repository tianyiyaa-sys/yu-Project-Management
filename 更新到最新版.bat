@echo off
chcp 65001 >nul
title 雨诺项目经营工作台 - 更新
cd /d "%~dp0"

echo.
echo ========================================
echo   更新雨诺项目经营工作台
echo ========================================
echo.

where git >nul 2>&1
if errorlevel 1 (
  echo 当前电脑没有检测到 Git。
  echo 先不用处理，把这个窗口截图发给我即可。
  pause
  exit /b 1
)

echo [1/3] 获取最新版代码...
git fetch origin yu-pmo-v1
git checkout yu-pmo-v1
git pull origin yu-pmo-v1
if errorlevel 1 (
  echo 更新代码失败，请截图发给我。
  pause
  exit /b 1
)

echo [2/3] 重新构建...
docker compose -f docker-compose.yml -f docker-compose.yu-local.yml up -d --build
if errorlevel 1 (
  echo 构建失败，请截图发给我。
  pause
  exit /b 1
)

echo [3/3] 完成。
start "" "http://localhost:3000"
echo.
echo 已更新到最新版。
pause
