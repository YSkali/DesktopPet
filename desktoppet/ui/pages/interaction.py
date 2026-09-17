# -*- coding: utf-8 -*-
"""互动页面：台词、待机自言自语与反应时长。"""

from ..registry import register
from ..widgets import ConfigPage


@register
class InteractionPage(ConfigPage):
    id = "interaction"
    title = "互动"
    order = 30
    description = "点击/拖拽台词、待机自言自语与反应时长，修改后即时生效。"
    fields = (
        {"key": "talk_on_click", "label": "互动时说话", "kind": "bool"},
        {"key": "idle_chatter", "label": "待机自言自语", "kind": "bool"},
        {"key": "chatter_interval", "label": "自言自语间隔", "kind": "int",
         "from": 5, "to": 120, "hint": "秒"},
        {"key": "click_reaction_ms", "label": "点击反应时长", "kind": "int",
         "from": 200, "to": 2000, "hint": "毫秒"},
    )
