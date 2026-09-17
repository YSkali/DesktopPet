# -*- coding: utf-8 -*-
"""从 OpenGameArt 的 CC0 精灵素材生成内置角色包。

数据来源（均为 CC0 公共领域授权）：
  - ScratchIO, "Animated Wild Animals" — https://opengameart.org/content/animated-wild-animals
      All.zip:    https://opengameart.org/sites/default/files/All.zip
  - ScratchIO, "Animated Horse"        — https://opengameart.org/content/animated-horse
      Horse.zip:  https://opengameart.org/sites/default/files/Horse.zip

素材是“单行横向帧条”（每帧左右以透明列分隔），本脚本按透明间隙切帧，
统一缩放并居中到 128x128 画布，按状态写入 pets/<name>/{idle,walk_left,click,drag}/NN.png，
同时生成 manifest.json。

用法：
    # 1) 准备源素材（解压到 --src 目录）
    mkdir -p /tmp/oga && cd /tmp/oga
    curl -L -o All.zip   https://opengameart.org/sites/default/files/All.zip
    curl -L -o Horse.zip https://opengameart.org/sites/default/files/Horse.zip
    unzip -o All.zip -d wild && unzip -o Horse.zip -d horse
    # 2) 生成角色包（默认写入 <项目>/pets）
    python scripts/build_packs_from_oga.py --src /tmp/oga
"""
import argparse
import json
import os

from PIL import Image

CANVAS = 128     # 与 config 默认 pet_size 一致
CONTENT = 116    # 内容框（四周留边约 6px）

# 每个角色包：idle / walk 源文件（相对 --src）
PACKS = [
    {"name": "deer",   "display": "小鹿",   "idle": "wild/Wild Animals/Deer/Deer_Idle.png",
     "walk": "wild/Wild Animals/Deer/Deer_Walk.png"},
    {"name": "bear",   "display": "小熊",   "idle": "wild/Wild Animals/Bear/Bear_Idle.png",
     "walk": "wild/Wild Animals/Bear/Bear_Walk.png"},
    {"name": "wolf",   "display": "小狼",   "idle": "wild/Wild Animals/Wolf/Wolf_Howl.png",
     "walk": "wild/Wild Animals/Wolf/Wolf_Walk.png"},
    {"name": "fox",    "display": "小狐狸", "idle": "wild/Wild Animals/Fox/Fox_Idle.png",
     "walk": "wild/Wild Animals/Fox/Fox_Walk.png"},
    {"name": "boar",   "display": "小野猪", "idle": "wild/Wild Animals/Boar/Boar_Idle.png",
     "walk": "wild/Wild Animals/Boar/Boar_Walk.png"},
    {"name": "rabbit", "display": "小兔子", "idle": "wild/Wild Animals/Rabbit/Rabbit_Idle.png",
     "walk": "wild/Wild Animals/Rabbit/Rabbit_Hop.png"},
    {"name": "horse",  "display": "小马",   "idle": "horse/Horse/Horse_Idle.png",
     "walk": "horse/Horse/Horse_Walk.png"},
]

AUTHOR = "ScratchIO (https://opengameart.org/users/scratchio)"
SOURCE = "https://opengameart.org"


def slice_strip(im):
    """按透明列间隙把单行帧条切成单帧（自动裁掉每帧四周空白）。"""
    rgba = im.convert("RGBA")
    w, h = rgba.size
    alpha = rgba.split()[3]
    cols = [alpha.crop((x, 0, x + 1, h)).getbbox() is not None for x in range(w)]
    segs, start = [], None
    for x, filled in enumerate(cols):
        if filled and start is None:
            start = x
        if not filled and start is not None:
            segs.append((start, x))
            start = None
    if start is not None:
        segs.append((start, w))

    frames = []
    for a, b in segs:
        cell = rgba.crop((a, 0, b, h))
        bbox = cell.split()[3].getbbox()
        if bbox:
            frames.append(cell.crop(bbox))
    return frames


def compute_scale(frame_sets, box=CONTENT):
    """各状态共用一个缩放比，保证角色在不同动作间大小一致。"""
    max_w = max(f.width for fs in frame_sets for f in fs)
    max_h = max(f.height for fs in frame_sets for f in fs)
    return min(box / max_w, box / max_h)


def place(frame, scale):
    """等比缩放并居中贴到透明画布上，采用 NEAREST 保留像素风锐利边缘。"""
    w = max(1, round(frame.width * scale))
    h = max(1, round(frame.height * scale))
    resized = frame.resize((w, h), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    canvas.paste(resized, ((CANVAS - w) // 2, (CANVAS - h) // 2), resized)
    return canvas


def build_pack(spec, src_root, out_root):
    idle_frames = slice_strip(Image.open(os.path.join(src_root, spec["idle"])))
    walk_frames = slice_strip(Image.open(os.path.join(src_root, spec["walk"])))
    if not idle_frames or not walk_frames:
        raise RuntimeError(f"{spec['name']}: 帧解析失败（检查源文件是否存在）")

    scale = compute_scale([idle_frames, walk_frames])
    drag_idx = len(walk_frames) // 2
    states = {
        "idle": idle_frames[:6],           # 2–8 帧
        "walk_left": walk_frames[:8],      # 4–8 帧（素材面朝左；向右走由引擎镜像）
        "click": idle_frames[:1],          # 1 帧
        "drag": walk_frames[drag_idx:drag_idx + 1] or idle_frames[:1],
    }

    pack_dir = os.path.join(out_root, spec["name"])
    for state, frames in states.items():
        dst = os.path.join(pack_dir, state)
        os.makedirs(dst, exist_ok=True)
        for i, fr in enumerate(frames, 1):
            place(fr, scale).save(os.path.join(dst, f"{i:02d}.png"), "PNG")

    manifest = {
        "name": spec["display"],
        "author": AUTHOR,
        "description": f"CC0 像素动物（{spec['display']}）· 来自 OpenGameArt",
        "license": "CC0",
        "source": SOURCE,
    }
    with open(os.path.join(pack_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    return {k: len(v) for k, v in states.items()}, scale


def main():
    parser = argparse.ArgumentParser(description="从 OpenGameArt CC0 素材生成角色包")
    default_out = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pets"
    )
    parser.add_argument("--src", required=True, help="解压后的源素材目录")
    parser.add_argument("--out", default=default_out, help="输出目录（默认 <项目>/pets）")
    parser.add_argument("--only", nargs="*", help="只生成指定角色包名")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    done = 0
    for spec in PACKS:
        if args.only and spec["name"] not in args.only:
            continue
        try:
            counts, scale = build_pack(spec, args.src, args.out)
        except (OSError, RuntimeError) as exc:
            print(f"[跳过] {spec['name']}: {exc}")
            continue
        done += 1
        print(f"[完成] {spec['name']:8} 缩放={scale:.2f}  帧数={counts}")
    print("-" * 48)
    print(f"共生成 {done} 个角色包 -> {args.out}")


if __name__ == "__main__":
    main()
