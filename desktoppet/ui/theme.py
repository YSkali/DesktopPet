# -*- coding: utf-8 -*-
"""控制台主题：颜色、字体与统一控件工厂。

所有页面共用这里的常量与工厂函数，保证视觉一致；调整外观只需改这一个文件。
工厂函数允许调用方覆盖任意默认样式（如 padx/pady），不会发生关键字冲突。
统一使用原生 ``tk`` 控件并显式着色，规避 Windows 主题下的对比度问题。
"""

import tkinter as tk

# ---------- 颜色 ----------
BG = "#1f1f1f"
FG = "#f5f5f5"
SUB = "#9a9a9a"
HEADER_BG = "#262626"
FOOTER_BG = "#181818"
NAV_BG = "#2a2a2a"
BTN_BG = "#3a3a3a"
FIELD_BG = "#2d2d2d"
SELECT = "#333333"
ACCENT = "#4a9eff"
ACCENT_FG = "#ffffff"
OK_FG = "#5fd67a"
ERR_FG = "#ff6b6b"
WARN_FG = "#f5c451"

# ---------- 字体 ----------
FAMILY = "Microsoft YaHei"
FONT = (FAMILY, 10)
FONT_BOLD = (FAMILY, 11, "bold")
FONT_TITLE = (FAMILY, 13, "bold")
FONT_SMALL = (FAMILY, 9)
FONT_MONO = ("Consolas", 9)


# ---------- 控件工厂 ----------
def _make(factory, parent, defaults, kw):
    opts = dict(defaults)
    opts.update(kw)
    return factory(parent, **opts)


def frame(parent, bg=BG, **kw):
    return _make(tk.Frame, parent, {"bg": bg}, kw)


def label(parent, text="", fg=FG, bg=BG, font=None, **kw):
    return _make(tk.Label, parent,
                 {"text": text, "fg": fg, "bg": bg, "font": font or FONT}, kw)


def button(parent, text, command=None, accent=False, **kw):
    defaults = {
        "text": text, "command": command, "relief": "flat", "bd": 0,
        "padx": 12, "pady": 6, "cursor": "hand2",
        "bg": ACCENT if accent else BTN_BG,
        "fg": ACCENT_FG if accent else FG,
        "activebackground": ACCENT, "activeforeground": ACCENT_FG,
    }
    return _make(tk.Button, parent, defaults, kw)


def entry(parent, textvariable=None, **kw):
    return _make(tk.Entry, parent,
                 {"textvariable": textvariable, "bg": FIELD_BG, "fg": FG,
                  "insertbackground": FG, "relief": "flat"}, kw)


def checkbutton(parent, variable, **kw):
    return _make(tk.Checkbutton, parent,
                 {"variable": variable, "bg": BG, "fg": FG,
                  "activebackground": BG, "activeforeground": FG,
                  "selectcolor": SELECT, "highlightthickness": 0,
                  "onvalue": 1, "offvalue": 0}, kw)


def scale(parent, variable, from_, to, resolution=1, length=260, **kw):
    return _make(tk.Scale, parent,
                 {"variable": variable, "from_": from_, "to": to,
                  "orient": "horizontal", "length": length, "bg": BG, "fg": FG,
                  "highlightthickness": 0, "troughcolor": SELECT,
                  "activebackground": ACCENT, "resolution": resolution}, kw)


__all__ = [
    "BG", "FG", "SUB", "HEADER_BG", "FOOTER_BG", "NAV_BG", "BTN_BG",
    "FIELD_BG", "SELECT", "ACCENT", "ACCENT_FG", "OK_FG", "ERR_FG", "WARN_FG",
    "FAMILY", "FONT", "FONT_BOLD", "FONT_TITLE", "FONT_SMALL", "FONT_MONO",
    "frame", "label", "button", "entry", "checkbutton", "scale",
]
