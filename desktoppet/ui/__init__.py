# -*- coding: utf-8 -*-
"""桌面控制台（页面式功能扩展框架）。

设计目标：**加功能 = 加一个页面模块**。

- :mod:`desktoppet.ui.theme`      —— 颜色 / 字体 / 控件工厂
- :mod:`desktoppet.ui.context`    —— PageContext（页面与主程序之间的桥梁）
- :mod:`desktoppet.ui.registry`   —— 页面注册表（Page / register / load_pages）
- :mod:`desktoppet.ui.widgets`    —— 字段构建器 + ConfigPage 基类
- :mod:`desktoppet.ui.panel`      —— 控制台窗口（导航 + 页面宿主）
- :mod:`desktoppet.ui.pages`      —— 内置页面集合

新增功能只需在 ``pages/`` 下放一个新模块并用 ``@register`` 注册，
控制台会自动发现，无需改动控制台本体。
"""

from . import theme
from .context import PageContext
from .panel import ControlPanel
from .registry import Page, get_pages, load_pages, register

__all__ = [
    "ControlPanel",
    "Page",
    "PageContext",
    "register",
    "get_pages",
    "load_pages",
    "theme",
]
