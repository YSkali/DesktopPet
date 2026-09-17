# -*- coding: utf-8 -*-
"""外观页面：大小、层级与透明度。"""

from ..registry import register
from ..widgets import ConfigPage


@register
class AppearancePage(ConfigPage):
    id = "appearance"
    title = "外观"
    order = 10
    description = "调整桌宠大小、层级与透明度。透明色修改后需重启生效。"
    fields = (
        {"key": "pet_size", "label": "宠物大小", "kind": "int",
         "from": 64, "to": 256, "hint": "像素，即时生效"},
        {"key": "opacity", "label": "不透明度", "kind": "float",
         "from": 0.2, "to": 1.0, "hint": "0.2–1.0，即时生效"},
        {"key": "topmost", "label": "始终置顶", "kind": "bool"},
        {"key": "transparent_color", "label": "透明色", "kind": "color",
         "hint": "如 #abcdef（重启生效）"},
    )
