# -*- coding: utf-8 -*-
"""通用页面：启动、素材与角色包设置。"""

from ..registry import register
from ..widgets import ConfigPage


@register
class GeneralPage(ConfigPage):
    id = "general"
    title = "通用"
    order = 15
    description = "启动、素材与角色包设置（目录/默认角色包改动需重启生效）。"
    fields = (
        {"key": "auto_prepare_assets", "label": "自动处理素材", "kind": "bool",
         "hint": "缺少处理后素材时自动生成"},
        {"key": "single_instance", "label": "单实例运行", "kind": "bool",
         "hint": "重启生效"},
        {"key": "pets_dir", "label": "角色包目录", "kind": "path",
         "hint": "重启生效"},
    )

    def get_fields(self, ctx):
        fields = list(super().get_fields(ctx))
        options = [""]
        labels = {"": "(内置素材)"}
        for pack in (getattr(ctx.pet, "packs", None) or []):
            name = getattr(pack, "name", "")
            if name:
                options.append(name)
                labels[name] = getattr(pack, "display_name", name)
        fields.append({
            "key": "pack", "label": "默认角色包", "kind": "choice",
            "options": options, "labels": labels, "hint": "启动时使用",
        })
        return fields
