#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""图片 → 桌宠 流水线 CLI。

把上传目录里的图片一键处理成角色包（自动分类动作状态、去背、统一尺寸）。

用法::

    python scripts/build_pet.py                 # 扫描 upload/ 下每个子目录，各生成一个角色包
    python scripts/build_pet.py upload/cat      # 只处理指定目录
    python scripts/build_pet.py upload/cat --name cat --display-name "咪咪" --author me
"""

import argparse
import logging
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from desktoppet.pipeline import build_pet  # noqa: E402

DEFAULT_UPLOAD = os.path.join(ROOT, "upload")
DEFAULT_PETS = os.path.join(ROOT, "pets")


def _build_one(source, name, pets_dir, args):
    try:
        result = build_pet(
            source,
            name,
            out_dir=pets_dir,
            display_name=args.display_name,
            author=args.author,
            description=args.description,
            remove_bg=not args.no_remove_bg,
            threshold=args.threshold,
            size=(args.size, args.size) if args.size else None,
        )
    except ValueError as e:
        print(f"  [跳过] {name}: {e}")
        return 0
    states = ", ".join(f"{k}×{v}" for k, v in result["states"].items())
    print(f"  [完成] {name}: {states}（共 {result['total']} 张）")
    return result["total"]


def main(argv=None):
    parser = argparse.ArgumentParser(description="图片 → 桌宠 流水线")
    parser.add_argument("source", nargs="?", default=None,
                        help="图片目录（留空则扫描 upload/ 下的所有子目录）")
    parser.add_argument("--name", default=None, help="角色包标识（默认取目录名）")
    parser.add_argument("--display-name", default=None, help="显示名称")
    parser.add_argument("--author", default="", help="作者")
    parser.add_argument("--description", default="", help="简介")
    parser.add_argument("--upload-dir", default=DEFAULT_UPLOAD, help="上传目录")
    parser.add_argument("--pets-dir", default=DEFAULT_PETS, help="角色包输出目录")
    parser.add_argument("--threshold", type=int, default=240, help="去白底阈值(0-255)")
    parser.add_argument("--size", type=int, default=None, help="输出边长（默认 128）")
    parser.add_argument("--no-remove-bg", action="store_true", help="不去除背景")
    parser.add_argument("--quiet", action="store_true", help="减少日志输出")
    args = parser.parse_args(argv)

    if not args.quiet:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    print("=" * 56)
    print(" 图片 → 桌宠 流水线 / Image → Pet Pipeline")
    print("=" * 56)

    total = 0
    if args.source:
        if not os.path.isdir(args.source):
            print(f"[错误] 目录不存在: {args.source}")
            return 1
        name = args.name or os.path.basename(os.path.normpath(args.source))
        print(f"来源: {args.source}")
        total += _build_one(args.source, name, args.pets_dir, args)
    else:
        if not os.path.isdir(args.upload_dir):
            print(f"[错误] 上传目录不存在: {args.upload_dir}")
            return 1
        subs = [
            d for d in sorted(os.listdir(args.upload_dir))
            if os.path.isdir(os.path.join(args.upload_dir, d))
            and not d.startswith(("_", "."))
        ]
        if not subs:
            print(f"upload/ 下暂无角色子目录。")
            print(f"请把图片放进 {os.path.join(args.upload_dir, '<角色名>')}/ 后重试。")
            print("（也支持文件名前缀，如 idle_01.png / walk_01.png / click.png）")
            return 0
        print(f"扫描到 {len(subs)} 个角色目录: {', '.join(subs)}")
        for d in subs:
            total += _build_one(os.path.join(args.upload_dir, d), d, args.pets_dir, args)

    print("-" * 56)
    print(f"完成，共生成 {total} 张帧。")
    print("重启桌宠后，右键菜单 → 切换角色 即可看到新宠物。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
