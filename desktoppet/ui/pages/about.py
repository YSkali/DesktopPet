# -*- coding: utf-8 -*-
"""关于页面：版本、当前状态与扩展说明。"""

from .. import theme
from ..registry import Page, register
from ...version import __version__


@register
class AboutPage(Page):
    id = "about"
    title = "关于"
    order = 90

    def build(self, parent, ctx):
        pet = ctx.pet
        lines = [f"DesktopPet v{__version__}", "", "一个可爱的桌面小伙伴。", ""]
        if pet is not None:
            mood = getattr(pet, "mood", None)
            lines.append(f"当前心情：{mood.label if mood else '--'}")
            lines.append(f"亲密度：{getattr(pet, 'affinity', 0)} 次互动")
            packs = getattr(pet, "packs", [])
            idx = getattr(pet, "active_pack", 0)
            if packs and 0 <= idx < len(packs):
                lines.append(f"当前角色：{packs[idx].display_name}")
        lines += ["", "左键拖拽移动 / 单击互动 / 双击抚摸 / 右键菜单"]

        theme.label(parent, "\n".join(lines), justify="left", anchor="w",
                    wraplength=460).pack(fill="x", padx=16, pady=16)
        theme.label(parent, justify="left", anchor="w", wraplength=460,
                    fg=theme.SUB, font=theme.FONT_SMALL,
                    text="扩展提示：加功能 = 加页面 —— 在 desktoppet/ui/pages/ "
                         "新建模块并用 @register 注册即可自动出现在此控制台。"
                    ).pack(fill="x", padx=16)
