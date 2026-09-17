# -*- coding: utf-8 -*-
"""素材预处理：统一尺寸、去白底、输出透明 PNG。

从图片四边向内做 flood fill，只去除与边缘相连的白色区域，
因此角色内部的白色（如眼睛、衣服）会被保留。
"""

import logging
import os
from collections import deque

from PIL import Image

logger = logging.getLogger(__name__)

TARGET_SIZE = (128, 128)

# 源子目录 -> 处理后子目录（命名保持一致，便于扩展）
ASSET_MAP = {
    "idle": "idle",
    "walk_left": "walk_left",
    "drag": "drag",
    "click": "click",
}

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")


def is_white_pixel(pixel, threshold=240):
    """判断像素是否接近白色（忽略 alpha 通道）。"""
    r, g, b = pixel[0], pixel[1], pixel[2]
    return r >= threshold and g >= threshold and b >= threshold


def remove_background_floodfill(img, threshold=240):
    """从四边向内 flood fill，去掉与边缘相连的白色背景。"""
    pixels = img.load()
    width, height = img.size
    visited = [[False] * width for _ in range(height)]
    queue = deque()

    # 起点：四条边上的白色像素
    for x in range(width):
        for y in (0, height - 1):
            if not visited[y][x] and is_white_pixel(pixels[x, y], threshold):
                visited[y][x] = True
                queue.append((x, y))
    for y in range(height):
        for x in (0, width - 1):
            if not visited[y][x] and is_white_pixel(pixels[x, y], threshold):
                visited[y][x] = True
                queue.append((x, y))

    # BFS：使用 deque.popleft()，避免 list.pop(0) 的 O(n) 开销
    while queue:
        x, y = queue.popleft()
        r, g, b = pixels[x, y][0], pixels[x, y][1], pixels[x, y][2]
        pixels[x, y] = (r, g, b, 0)
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and not visited[ny][nx]:
                if is_white_pixel(pixels[nx, ny], threshold):
                    visited[ny][nx] = True
                    queue.append((nx, ny))
    return img


def process_image(input_path, output_path, remove_bg=True, bg_threshold=240, size=None):
    """处理单张图片：统一尺寸 -> RGBA -> 去白底 -> 保存 PNG。"""
    try:
        img = Image.open(input_path)
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        img = img.resize(size or TARGET_SIZE, Image.Resampling.LANCZOS)
        if remove_bg:
            img = remove_background_floodfill(img, bg_threshold)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, "PNG")
        return True
    except (OSError, ValueError) as e:
        logger.warning("处理失败 %s: %s", os.path.basename(input_path), e)
        return False


def process_folder(src_dir, dst_dir):
    """处理一个文件夹，输出统一命名为 01.png、02.png ... 返回成功数量。"""
    if not os.path.isdir(src_dir):
        return 0
    files = sorted(
        f for f in os.listdir(src_dir)
        if f.lower().endswith(IMAGE_EXTS)
    )
    count = 0
    for i, filename in enumerate(files, 1):
        input_path = os.path.join(src_dir, filename)
        output_path = os.path.join(dst_dir, f"{i:02d}.png")
        if process_image(input_path, output_path):
            count += 1
    return count


def prepare_all(src_root, dst_root):
    """处理全部素材，返回处理成功的图片总数。"""
    total = 0
    for src_name, dst_name in ASSET_MAP.items():
        src = os.path.join(src_root, src_name)
        dst = os.path.join(dst_root, dst_name)
        if os.path.isdir(src):
            n = process_folder(src, dst)
            total += n
            logger.info("处理 %-10s -> %s (%d 张)", src_name, dst_name, n)
        else:
            logger.info("跳过（目录不存在）: %s", src)
    return total


__all__ = [
    "TARGET_SIZE",
    "ASSET_MAP",
    "process_image",
    "process_folder",
    "prepare_all",
    "remove_background_floodfill",
]
