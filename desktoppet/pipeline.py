# -*- coding: utf-8 -*-
"""图片 → 桌宠 流水线。

把上传的图片自动分类到各动作状态（待机 / 走路 / 点击 / 拖拽 / 抚摸），
去背、统一尺寸后生成一个角色包 ``pets/<name>/``，重启即可在右键菜单切换。

支持三种上传组织方式（可混用）::

    upload/my_pet/idle/01.png            # ① 状态子目录
    upload/my_pet/idle_01.png            # ② 文件名前缀
    upload/my_pet/01.png                 # ③ 无提示 → 归为 idle

状态别名同时支持英文与中文（如 待机 / 走 / 点击 / 拖拽 / 抚摸）。
"""

import json
import logging
import os

from .prepare import IMAGE_EXTS, TARGET_SIZE, process_image

logger = logging.getLogger(__name__)

# 规范状态（与 pet.py 的状态名一致）
STATES = ("idle", "walk_left", "click", "drag", "pet")
DEFAULT_STATE = "idle"

# 各状态的别名（英文 / 中文 / 常见写法）
STATE_ALIASES = {
    "idle": ("idle", "stand", "stay", "wait", "待机", "待機", "静止", "站立", "站着"),
    "walk_left": ("walk_left", "walkleft", "walk", "left", "走", "行走", "向左走", "左走", "移动"),
    "click": ("click", "tap", "hit", "点击", "點擊", "被点击", "戳"),
    "drag": ("drag", "draging", "拖拽", "拖", "被拖拽", "拎起", "提起"),
    "pet": ("pet", "pat", "抚摸", "撫摸", "摸头", "摸摸", "被摸"),
}

# 用于把文件名/目录名切成 token 的分隔符
_SPLIT_CHARS = "_- .·、,，()（）[]【】#@!＋+"


def _norm(text):
    return (text or "").strip().lower()


def _tokens(text):
    out, cur = [], ""
    for ch in text:
        if ch in _SPLIT_CHARS:
            if cur:
                out.append(cur)
                cur = ""
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


def classify_state(hint):
    """把文件名或目录名映射为动作状态；无法判断返回 None。"""
    h = _norm(hint)
    if not h:
        return None
    if h in STATES:
        return h
    # 整串别名匹配
    for state, aliases in STATE_ALIASES.items():
        if h in aliases:
            return state
    # 逐 token 匹配
    for token in _tokens(h):
        for state, aliases in STATE_ALIASES.items():
            if token in aliases:
                return state
    # 子串兜底（至少 2 个字符）
    for state, aliases in STATE_ALIASES.items():
        for alias in aliases:
            if len(alias) >= 2 and alias in h:
                return state
    return None


def _strict_state(hint):
    """整串精确匹配状态（用于目录名），不做 token/子串猜测。"""
    h = _norm(hint)
    if not h:
        return None
    if h in STATES:
        return h
    for state, aliases in STATE_ALIASES.items():
        if h in aliases:
            return state
    return None


def detect_state(file_path, root=None):
    """判断图片状态：优先“状态子目录”，其次“文件名前缀”，判断不了返回 None。

    root 为角色包根目录时，与其同名的父目录不作为状态目录，
    避免把包名（如 ``my_pet``）误判为状态。
    """
    parent = os.path.basename(os.path.dirname(file_path))
    stem = os.path.splitext(os.path.basename(file_path))[0]
    root_name = os.path.basename(os.path.normpath(root)) if root else None
    if not (root_name and parent == root_name):
        state = _strict_state(parent)
        if state:
            return state
    return classify_state(stem) or None


def collect_images(source):
    """递归收集 source 下所有图片，按路径排序返回。"""
    files = []
    for root, _dirs, names in os.walk(source):
        for name in names:
            if name.lower().endswith(IMAGE_EXTS):
                files.append(os.path.join(root, name))
    files.sort()
    return files


def build_pet(source, name, out_dir="pets", display_name=None, author="",
              description="", remove_bg=True, threshold=240, size=None):
    """把 source 下的图片处理成角色包，返回统计信息 dict。

    :returns: {"name", "path", "states": {state: count}, "total"}
    """
    files = collect_images(source)
    if not files:
        raise ValueError(f"未找到任何图片: {source}")

    target = os.path.join(out_dir, name)
    counters = {}
    summary = {}

    for path in files:
        state = detect_state(path, root=source) or DEFAULT_STATE
        counters[state] = counters.get(state, 0) + 1
        dst = os.path.join(target, state, f"{counters[state]:02d}.png")
        if process_image(path, dst, remove_bg=remove_bg,
                         bg_threshold=threshold, size=size):
            summary[state] = summary.get(state, 0) + 1
        else:
            logger.warning("处理失败: %s", path)

    os.makedirs(target, exist_ok=True)
    manifest = {
        "name": (display_name or name).strip(),
        "author": author,
        "description": description,
    }
    with open(os.path.join(target, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    total = sum(summary.values())
    logger.info("角色包 %s 生成完成: %s (共 %d 张)", name, summary, total)
    return {"name": name, "path": target, "states": summary, "total": total}


__all__ = [
    "STATES",
    "STATE_ALIASES",
    "DEFAULT_STATE",
    "classify_state",
    "detect_state",
    "collect_images",
    "build_pet",
]
