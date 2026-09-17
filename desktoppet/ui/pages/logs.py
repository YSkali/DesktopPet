# -*- coding: utf-8 -*-
"""日志页面：查看运行日志并可打开日志目录。"""

import os
import tkinter as tk

from ..._paths import log_dir, log_file, open_path
from .. import theme
from ..registry import Page, register


@register
class LogsPage(Page):
    id = "logs"
    title = "日志"
    order = 70

    def build(self, parent, ctx):
        self.ctx = ctx
        bar = theme.frame(parent)
        bar.pack(fill="x", padx=16, pady=(14, 6))
        theme.label(bar, "运行日志", font=theme.FONT_BOLD).pack(side="left")
        theme.button(bar, "↻ 刷新", self.refresh).pack(side="right")
        theme.button(bar, "📂 日志目录",
                     lambda: open_path(log_dir())).pack(side="right", padx=6)

        wrap = theme.frame(parent)
        wrap.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self._text = tk.Text(wrap, bg=theme.FIELD_BG, fg=theme.FG, bd=0,
                             insertbackground=theme.FG, font=theme.FONT_MONO,
                             wrap="none", height=16)
        yscroll = tk.Scrollbar(wrap, command=self._text.yview)
        xscroll = tk.Scrollbar(wrap, orient="horizontal",
                               command=self._text.xview)
        self._text.configure(yscrollcommand=yscroll.set,
                             xscrollcommand=xscroll.set)
        yscroll.pack(side="right", fill="y")
        xscroll.pack(side="bottom", fill="x")
        self._text.pack(side="left", fill="both", expand=True)
        self.refresh()

    def refresh(self):
        path = log_file()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()
                content = "".join(lines[-400:])
            except OSError as e:
                content = f"（无法读取日志：{e}）"
        else:
            content = "（暂无日志文件）\n\n日志会写入：\n" + path
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.insert("1.0", content)
        self._text.see("end")
        self._text.configure(state="disabled")
