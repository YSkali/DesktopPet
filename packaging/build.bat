@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo ========================================
echo 桌宠打包工具 DesktopPet Builder
echo ========================================
echo.

echo [1/3] 检查依赖...
python -c "import PIL, cx_Freeze" 2>nul
if errorlevel 1 (
    echo 正在安装依赖：pip install -r requirements.txt -r requirements-dev.txt
    pip install -r requirements.txt -r requirements-dev.txt
)
echo.

echo [2/3] 处理素材...
python scripts\prepare_assets.py
echo.

echo [3/3] 打包，请稍候（可能需要 1-2 分钟）...
python packaging\setup_cx.py build
echo.

echo ========================================
if exist "build\exe.*\DesktopPet.exe" (
    echo [完成] 打包成功！
    echo 文件位置: build\exe.*\
    echo.
    echo 你可以：
    echo   1. 进入 build\exe.*\ 目录
    echo   2. 双击 DesktopPet.exe 运行
    echo   3. 将整个文件夹复制到 U 盘使用
) else (
    echo [错误] 打包失败，请检查上方错误信息
)
echo ========================================
pause
