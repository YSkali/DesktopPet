# -*- coding: utf-8 -*-
"""角色包（Character Pack）系统。

一个“角色包”是 ``pets/`` 下的一个子目录，里面按状态存放 PNG 帧::

    pets/
    └── my_pet/
        ├── manifest.json     # 可选，描述名称/作者等
        ├── idle/01.png ...
        ├── walk_left/01.png ...
        ├── click/01.png ...
        └── drag/01.png ...

- 目录名以 ``_`` 或 ``.`` 开头的会被忽略（可放模板）。
- 角色包缺失的状态，程序会自动回退到内置默认素材。
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

STATES = ("idle", "walk_left", "drag", "click")
MANIFEST_NAME = "manifest.json"


class Pack:
    """一个角色包。"""

    def __init__(self, name, path, manifest=None):
        self.name = name            # 目录名 / 标识
        self.path = path            # 绝对路径
        self.manifest = manifest or {}

    @property
    def display_name(self):
        return (self.manifest.get("name") or self.name).strip()

    @property
    def author(self):
        return self.manifest.get("author", "")

    @property
    def description(self):
        return self.manifest.get("description", "")

    def state_dir(self, state):
        return os.path.join(self.path, state)

    def has_state(self, state):
        d = self.state_dir(state)
        if not os.path.isdir(d):
            return False
        return any(f.lower().endswith(".png") for f in os.listdir(d))

    def available_states(self):
        return [s for s in STATES if self.has_state(s)]

    def __repr__(self):
        return f"<Pack {self.name!r} at {self.path}>"


def load_manifest(pack_dir):
    """读取目录下的 manifest.json，不存在或损坏时返回 {}。"""
    path = os.path.join(pack_dir, MANIFEST_NAME)
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError) as e:
        logger.warning("角色包 manifest 读取失败 %s: %s", path, e)
        return {}


def discover_packs(pets_dir):
    """扫描 pets_dir 下所有含有效帧的子目录，返回 Pack 列表（按名称排序）。"""
    packs = []
    if not os.path.isdir(pets_dir):
        return packs
    for entry in sorted(os.listdir(pets_dir)):
        if entry.startswith("_") or entry.startswith("."):
            continue  # 跳过模板/隐藏目录
        pack_dir = os.path.join(pets_dir, entry)
        if not os.path.isdir(pack_dir):
            continue
        pack = Pack(entry, pack_dir, load_manifest(pack_dir))
        if pack.available_states():
            packs.append(pack)
        else:
            logger.warning("跳过无效角色包（无可用帧）: %s", pack_dir)
    return packs


__all__ = ["Pack", "discover_packs", "load_manifest", "STATES"]
