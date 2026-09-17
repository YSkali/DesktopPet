# -*- coding: utf-8 -*-
"""控制台通用控件：字段构建器 + 配置页基类。

对外统一出口，页面只需 ``from ..widgets import ConfigPage``。
"""

from .. import theme
from .fields import BUILDERS, _coerce, build_field, coerce
from .form import ConfigPage

# 主题便捷别名（保持与旧模块路径的兼容）
make_button = theme.button
BG = theme.BG
FG = theme.FG
SUB = theme.SUB
ACCENT = theme.ACCENT
OK_FG = theme.OK_FG
ERR_FG = theme.ERR_FG

__all__ = [
    "ConfigPage",
    "build_field",
    "BUILDERS",
    "coerce",
    "_coerce",
    "make_button",
    "BG",
    "FG",
    "SUB",
    "ACCENT",
    "OK_FG",
    "ERR_FG",
]
