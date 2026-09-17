# -*- coding: utf-8 -*-
"""素材预处理入口：把 assets/ 处理成 assets_processed/。

用法::

    python scripts/prepare_assets.py
"""

import logging
import os
import sys

# 让脚本能直接 import 到项目里的 desktoppet 包
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from desktoppet.prepare import prepare_all  # noqa: E402


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    src = os.path.join(ROOT, "assets")
    dst = os.path.join(ROOT, "assets_processed")

    print("=" * 50)
    print("桌宠素材预处理")
    print("=" * 50)

    if not os.path.isdir(src):
        print(f"[错误] 找不到素材目录: {src}")
        return 1

    total = prepare_all(src, dst)

    print("=" * 50)
    print(f"处理完成！共 {total} 张图片")
    print(f"输出目录: {dst}")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main())
