@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在执行自检...
echo.
python scripts\check.py %*
echo.
pause
