# -*- coding: utf-8 -*-
"""动作页面：移动速度、动画节奏与休息概率。"""

from ..registry import register
from ..widgets import ConfigPage


@register
class MotionPage(ConfigPage):
    id = "motion"
    title = "动作"
    order = 20
    description = "走路速度、动画节奏与休息概率，修改后即时生效。"
    fields = (
        {"key": "move_speed", "label": "移动速度", "kind": "int",
         "from": 1, "to": 10, "hint": "每次像素"},
        {"key": "movement_interval", "label": "移动间隔", "kind": "int",
         "from": 20, "to": 300, "hint": "毫秒"},
        {"key": "anim_speed", "label": "待机动画", "kind": "int",
         "from": 100, "to": 1000, "hint": "毫秒/帧"},
        {"key": "walk_anim_speed", "label": "走路动画", "kind": "int",
         "from": 100, "to": 1000, "hint": "毫秒/帧"},
        {"key": "rest_chance", "label": "休息概率", "kind": "float",
         "from": 0.0, "to": 1.0},
        {"key": "edge_bounce", "label": "边缘弹跳", "kind": "bool",
         "hint": "走到屏幕边缘时蹦一下"},
        {"key": "edge_pause_ms", "label": "边缘停顿", "kind": "int",
         "from": 0, "to": 2000, "hint": "撞边后停顿（毫秒）"},
    )
