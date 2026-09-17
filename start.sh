#!/usr/bin/env bash
# DesktopPet 一键启动（macOS / Linux）
set -e
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[错误] 未检测到 python3，请先安装 Python 3.9+"
  exit 1
fi

if ! python3 -c "import PIL" >/dev/null 2>&1; then
  echo "[1/2] 首次运行，正在安装依赖..."
  python3 -m pip install -r requirements.txt
fi

echo "[2/2] 正在启动桌宠..."
echo "操作: 左键拖动 / 单击互动 / 双击抚摸 / 右键菜单"
python3 run.py
