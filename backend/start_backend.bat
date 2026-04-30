# 后端启动脚本
@echo off
echo 正在启动智能手写笔记转录系统后端服务...
echo.
cd /d %~dp0
python app.py
pause
