@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   图片 -^> 桌宠 流水线
echo ========================================
echo.
echo 请先把图片放进 upload\^<角色名^\>\ 目录。
echo.
pause
python scripts\build_pet.py
echo.
pause
