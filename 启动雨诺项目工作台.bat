@echo off
chcp 65001 >nul
title 雨诺项目经营工作台 - 本地启动
cd /d "%~dp0"

echo.
echo ========================================
echo   雨诺项目经营工作台 - 本地测试环境
echo ========================================
echo.
echo [1/3] 检查 Docker...
docker version >nul 2>&1
if errorlevel 1 (
  echo.
  echo Docker Desktop 没有启动。
  echo 请先打开 Docker Desktop，等左下角显示 Engine running 后再双击本文件。
  echo.
  pause
  exit /b 1
)

echo [2/3] 构建并启动项目...
echo 第一次运行需要下载和构建，时间会比较长，以后会快很多。
docker compose -f docker-compose.yml -f docker-compose.yu-local.yml up -d --build
if errorlevel 1 (
  echo.
  echo 启动失败。请把这个窗口截图发给我，我来处理。
  echo.
  pause
  exit /b 1
)

echo [3/3] 等待服务启动...
timeout /t 8 /nobreak >nul

echo.
echo 已启动，正在打开浏览器：
echo http://localhost:3000
start "" "http://localhost:3000"
echo.
echo 如果页面暂时打不开，请等 30-60 秒后刷新。
echo 这个窗口可以关闭，不影响项目运行。
echo.
pause
