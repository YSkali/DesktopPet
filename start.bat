@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   桌面宠物 DesktopPet 一键启动
echo ========================================
echo.

REM ---- 1) 检查 Python ----
where python >nul 2>nul
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.9+ 并勾选 "Add Python to PATH"
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM ---- 2) 检查依赖，缺失则自动安装 ----
python -c "import PIL" >nul 2>nul
if errorlevel 1 (
    echo [1/2] 首次运行，正在安装依赖...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请检查网络后重试。
        pause
        exit /b 1
    )
)

REM ---- 3) 启动（程序会自动处理素材）----
echo [2/2] 正在启动桌宠...
echo 操作: 左键拖动 / 单击互动 / 双击抚摸 / 右键菜单 / 右键退出
echo.
python run.py

echo.
echo 桌宠已退出。
pause
