# -*- coding: utf-8 -*-
"""角色包页面：列出并切换 pets/ 下的角色包。"""

import tkinter as tk

from ...packs import discover_packs
from .. import theme
from ..registry import Page, register


@register
class PacksPage(Page):
    id = "packs"
    title = "角色包"
    order = 50

    def build(self, parent, ctx):
        self.ctx = ctx
        top = theme.frame(parent)
        top.pack(fill="x", padx=16, pady=(14, 4))
        theme.label(top, "角色包（pets/）", font=theme.FONT_BOLD).pack(side="left")

        self._list = theme.frame(parent)
        self._list.pack(fill="both", expand=True, padx=16, pady=6)

        bar = theme.frame(parent)
        bar.pack(fill="x", padx=16, pady=10)
        theme.button(bar, "↻ 刷新", self.refresh).pack(side="left")
        self._hint = theme.label(bar, "", fg=theme.SUB, font=theme.FONT_SMALL)
        self._hint.pack(side="left", padx=10)
        theme.label(parent, "切换后立即生效；可在 upload/ 放图后用 build_pet 生成新角色包",
                    fg=theme.SUB, font=theme.FONT_SMALL, anchor="w",
                    justify="left", wraplength=480).pack(
            fill="x", padx=16, pady=(0, 10))
        self.refresh()

    def _visible_packs(self):
        pet = self.ctx.pet
        packs = getattr(pet, "packs", None)
        if packs:
            return list(packs)
        # 没有主程序（例如单独测试）时，退化为直接扫描 pets/
        return discover_packs("pets")

    def refresh(self):
        for child in self._list.winfo_children():
            child.destroy()
        packs = self._visible_packs()
        if not packs:
            theme.label(self._list, anchor="w", fg=theme.SUB,
                        font=theme.FONT_SMALL, wraplength=480, justify="left",
                        text="（未检测到角色包；可在 upload/ 放图后运行 "
                             "build_pet 生成）").pack(fill="x")
            return
        active = getattr(self.ctx.pet, "active_pack", 0)
        for i, pack in enumerate(packs):
            current = i == active
            text = ("● " if current else "○ ") + pack.display_name
            author = getattr(pack, "author", "")
            if author:
                text += f"   · {author}"
            if current:
                text += "   （当前）"
            tk.Button(self._list, text=text, anchor="w", relief="flat", bd=0,
                      padx=10, pady=6,
                      bg=theme.ACCENT if current else theme.BG,
                      fg="white" if current else theme.FG, cursor="hand2",
                      activebackground=theme.ACCENT, activeforeground="white",
                      command=lambda i=i: self._switch(i)).pack(fill="x", pady=1)

    def _switch(self, index):
        self.ctx.switch_pack(index)
        if self._hint is not None:
            self._hint.configure(text="✓ 已切换", fg=theme.OK_FG)
        self.ctx.notify("已切换角色包", ok=True)
        self.ctx.say("换装完成 🎭")
        self.refresh()
