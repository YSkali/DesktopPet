# -*- coding: utf-8 -*-
"""感知页面：系统感知（CPU/时间）与启动问候。"""

from ..registry import register
from ..widgets import ConfigPage


@register
class AwarenessPage(ConfigPage):
    id = "awareness"
    title = "感知"
    order = 40
    description = "根据 CPU / 内存 / 电池与时间调整心情；影响移动与动画节奏。"
    fields = (
        {"key": "awareness", "label": "启用系统感知", "kind": "bool"},
        {"key": "greetings", "label": "启动打招呼", "kind": "bool"},
        {"key": "awareness_interval", "label": "感知间隔", "kind": "int",
         "from": 5, "to": 120, "hint": "秒"},
        {"key": "awareness_memory", "label": "内存感知", "kind": "bool",
         "hint": "内存吃紧时变忙"},
        {"key": "awareness_battery", "label": "电池感知", "kind": "bool",
         "hint": "低电量时提醒充电"},
    )
