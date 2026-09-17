# -*- coding: utf-8 -*-
"""动画帧的加载与切换。

不再硬编码帧数：自动扫描素材目录下的所有 PNG（按文件名排序），
所以用户增减素材图片后无需修改代码。
"""

import logging
import os

from PIL import Image

logger = logging.getLogger(__name__)


class AnimationManager:
    """负责加载和切换动画帧。"""

    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.animations = {}       # 动画名称 -> [帧列表]
        self.current_anim = None
        self.current_frame = 0

    def load_animation(self, name, folder):
        """自动扫描 folder 下的所有 PNG 作为动画帧，返回帧数。"""
        directory = os.path.join(self.base_dir, folder)
        frames = []
        if os.path.isdir(directory):
            files = sorted(
                f for f in os.listdir(directory)
                if f.lower().endswith(".png")
            )
            for filename in files:
                path = os.path.join(directory, filename)
                try:
                    img = Image.open(path)
                    if img.mode != "RGBA":
                        img = img.convert("RGBA")
                    frames.append(img)
                except (OSError, ValueError) as e:
                    logger.warning("帧加载失败 %s: %s", path, e)

        if frames:
            self.animations[name] = frames
            logger.info("已加载动画 %-10s: %d 帧", name, len(frames))
        else:
            logger.warning("动画 %s 无可用帧（目录: %s）", name, directory)
        return len(frames)

    def has(self, name):
        return name in self.animations

    def clear(self):
        """清空全部已加载动画（切换角色包时使用）。"""
        self.animations.clear()
        self.current_anim = None
        self.current_frame = 0

    def set_animation(self, name):
        """切换到指定动画（从头播放）。"""
        if name != self.current_anim and name in self.animations:
            self.current_anim = name
            self.current_frame = 0

    def get_current_frame(self):
        if self.current_anim and self.current_anim in self.animations:
            frames = self.animations[self.current_anim]
            if frames:
                return frames[self.current_frame % len(frames)]
        return None

    def next_frame(self):
        if self.current_anim and self.current_anim in self.animations:
            frames = self.animations[self.current_anim]
            if frames:
                self.current_frame = (self.current_frame + 1) % len(frames)


__all__ = ["AnimationManager"]
