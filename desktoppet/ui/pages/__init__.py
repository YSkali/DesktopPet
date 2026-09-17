# -*- coding: utf-8 -*-
"""内置控制台页面集合。

导入各页面模块即触发 ``@register`` 注册。**新增功能 = 加一个模块**，
然后在这里 import 一下即可（顺序不影响显示，显示按各页 order 排序）。
"""

from . import (  # noqa: F401
    about,
    appearance,
    awareness,
    general,
    interaction,
    logs,
    motion,
    packs,
    tools,
)

__all__ = [
    "appearance",
    "general",
    "motion",
    "interaction",
    "awareness",
    "packs",
    "tools",
    "logs",
    "about",
]
