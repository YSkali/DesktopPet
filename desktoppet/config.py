# -*- coding: utf-8 -*-
"""配置管理：支持外部 config.json，缺省时使用内置默认值。

用户无需修改源码，只要在项目根目录创建 config.json 即可自定义行为。
"""

import json
import logging
import os

from ._paths import app_dir

logger = logging.getLogger(__name__)

DEFAULTS = {
    # 外观
    "pet_size": 128,              # 宠物窗口边长（像素）
    "topmost": True,             # 是否始终置顶
    "opacity": 1.0,              # 窗口不透明度（0.2–1.0）
    "transparent_color": "#abcdef",  # 透明色键（Windows 专用）
    # 动画速度（毫秒，数值越大越慢）
    "anim_speed": 400,           # 待机动画间隔
    "walk_anim_speed": 300,      # 走路动画间隔
    # 移动
    "move_speed": 2,             # 每次移动像素
    "movement_interval": 80,     # 移动更新间隔（毫秒）
    "rest_chance": 0.3,          # 走一段后停下来休息的概率
    # 屏幕边缘行为
    "edge_bounce": True,         # 走到屏幕边缘时弹跳一下
    "edge_pause_ms": 400,        # 撞到边缘后短暂停顿的时间（毫秒）
    # 交互
    "click_reaction_ms": 800,    # 点击反应持续时间（毫秒）
    # 行为
    "auto_prepare_assets": True, # 缺少处理后素材时自动生成
    "single_instance": True,     # 是否只允许运行一个实例
    # 角色包
    "pack": "",            # 默认角色包名（空 = 使用内置素材 assets_processed）
    "pets_dir": "pets",    # 角色包目录
    # 系统感知
    "awareness": True,           # 根据 CPU 负载 / 时间调整行为
    "greetings": True,           # 启动时打招呼
    "awareness_interval": 15,    # 重新感知的间隔（秒）
    "awareness_memory": True,    # 把内存占用也纳入心情判断
    "awareness_battery": True,   # 把电池电量也纳入心情判断
    # 交互丰富度
    "talk_on_click": True,       # 点击 / 拖拽时说话
    "idle_chatter": True,        # 待机时偶尔自言自语
    "chatter_interval": 25,      # 自言自语间隔（秒）
}


class Config:
    """轻量配置对象。

    用法::

        cfg = Config()
        speed = cfg.get("move_speed")
    """

    def __init__(self, path=None):
        self.path = path or os.path.join(app_dir(), "config.json")
        self._data = dict(DEFAULTS)
        self.load()

    def load(self):
        """加载用户配置，未知字段会被忽略。"""
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                user = json.load(f)
            if isinstance(user, dict):
                for key, value in user.items():
                    if key in DEFAULTS:
                        self._data[key] = value
                    else:
                        logger.warning("忽略未知配置项: %s", key)
                logger.info("已加载配置: %s", self.path)
        except (OSError, ValueError) as e:
            logger.warning("配置文件读取失败，使用默认值: %s", e)

    def load_from(self, path):
        """从指定文件读取并合并配置（保留默认值，忽略未知键）。"""
        if not path or not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, "r", encoding="utf-8") as f:
            user = json.load(f)
        if not isinstance(user, dict):
            raise ValueError("配置内容不是 JSON 对象")
        for key, value in user.items():
            if key in DEFAULTS:
                self._data[key] = value
            else:
                logger.warning("导入时忽略未知配置项: %s", key)
        logger.info("已从 %s 导入配置", path)

    def save(self, path=None):
        """把当前配置写入文件并返回是否成功。

        会确保目标目录存在；任何写入/序列化错误都只记录日志并返回 False，
        不抛出异常，方便调用方（如控制台）据此给出明确反馈。
        """
        target = path or self.path
        try:
            parent = os.path.dirname(target)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            logger.info("已写入配置: %s", target)
            return True
        except (OSError, TypeError, ValueError) as e:
            logger.warning("配置写入失败: %s", e)
            return False

    def get(self, key):
        return self._data.get(key, DEFAULTS.get(key))

    def set(self, key, value):
        """写入一个配置项（仅内存，需 save() 落盘）。未知键返回 False。"""
        if key in DEFAULTS:
            self._data[key] = value
            return True
        logger.warning("忽略未知配置项: %s", key)
        return False

    def __getitem__(self, key):
        return self.get(key)


__all__ = ["Config", "DEFAULTS"]
