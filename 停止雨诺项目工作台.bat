@echo off
chcp 65001 >nul
title 雨诺项目经营工作台 - 停止
cd /d "%~dp0"
echo 正在停止雨诺项目经营工作台...
docker compose -f docker-compose.yml -f docker-compose.yu-local.yml down
echo.
echo 已停止。
timeout /t 2 /nobreak >nul
