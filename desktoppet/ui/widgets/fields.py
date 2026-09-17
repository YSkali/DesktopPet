# -*- coding: utf-8 -*-
"""配置字段：类型化构建器。

每个构建器签名 ``(parent, spec, value, ctx) -> (widget, tk_var)``。
支持的类型（``spec['kind']``）：

- ``bool``   复选框（0/1）
- ``int`` / ``float``  滑块
- ``str``    文本框
- ``color``  文本框 + 色块 + 取色彩板
- ``choice`` 下拉菜单（``options`` 为取值列表，``labels`` 可映射显示名）
- ``path``   目录选择（文本框 + 浏览）

新增字段类型只需实现构建器并登记到 :data:`BUILDERS`。
"""

import logging
import os
import tkinter as tk

from .. import theme

logger = logging.getLogger(__name__)


def coerce(kind, value, default):
    """把控件给出的值转成配置应有的类型。"""
    try:
        if kind == "int":
            return int(float(value))
        if kind == "float":
            return float(value)
        if kind == "bool":
            return bool(int(value))
    except (TypeError, ValueError):
        return default
    return value


_coerce = coerce  # 兼容旧名称


def _bool(parent, spec, value, ctx):
    var = tk.IntVar(value=1 if value else 0)
    return theme.checkbutton(parent, var), var


def _num(parent, spec, value, ctx):
    kind = spec.get("kind", "int")
    try:
        init = float(value)
    except (TypeError, ValueError):
        init = float(spec.get("from", 0))
    var = tk.DoubleVar(value=init)
    widget = theme.scale(parent, var, spec.get("from", 0), spec.get("to", 100),
                         resolution=1 if kind == "int" else 0.05)
    return widget, var


def _text(parent, spec, value, ctx):
    var = tk.StringVar(value="" if value is None else str(value))
    widget = theme.entry(parent, var, width=spec.get("width", 22))
    return widget, var


def _color(parent, spec, value, ctx):
    holder = theme.frame(parent)
    var = tk.StringVar(value="" if value is None else str(value))
    entry = theme.entry(holder, var, width=12)
    entry.pack(side="left", ipady=3)
    swatch = tk.Label(holder, width=2, bg=value or "#ffffff", bd=0)
    swatch.pack(side="left", padx=(6, 4), ipady=6)

    def sync(*_a):
        try:
            swatch.configure(bg=var.get().strip() or "#ffffff")
        except tk.TclError:
            pass

    var.trace_add("write", sync)

    def pick():
        from tkinter import colorchooser
        _rgb, hexv = colorchooser.askcolor(color=var.get() or "#ffffff")
        if hexv:
            var.set(hexv)

    theme.button(holder, "取色", pick, padx=8, pady=2).pack(side="left")
    return holder, var


def _choice(parent, spec, value, ctx):
    options = list(spec.get("options", []))
    labels = dict(spec.get("labels", {}))

    def lab(v):
        return labels.get(v, v if v != "" else "(默认)")

    var = tk.StringVar(value="" if value is None else str(value))
    mb = tk.Menubutton(holder_parent := parent, text=lab(var.get()),
                       bg=theme.FIELD_BG, fg=theme.FG, relief="flat", bd=0,
                       padx=10, pady=4, cursor="hand2", highlightthickness=0,
                       activebackground=theme.ACCENT,
                       activeforeground=theme.ACCENT_FG)
    menu = tk.Menu(mb, tearoff=0)

    def choose(v):
        var.set(v)
        mb.configure(text=lab(v))

    for v in options:
        menu.add_command(label=lab(v), command=lambda v=v: choose(v))
    mb.configure(menu=menu)
    return mb, var


def _path(parent, spec, value, ctx):
    holder = theme.frame(parent)
    var = tk.StringVar(value="" if value is None else str(value))
    entry = theme.entry(holder, var, width=spec.get("width", 20))
    entry.pack(side="left", fill="x", expand=True, ipady=3)

    def browse():
        from tkinter import filedialog
        chosen = filedialog.askdirectory(initialdir=var.get() or os.getcwd(),
                                         title=spec.get("label", "选择目录"))
        if chosen:
            var.set(chosen)

    theme.button(holder, "浏览…", browse, padx=8, pady=2).pack(
        side="left", padx=(6, 0))
    return holder, var


BUILDERS = {
    "bool": _bool,
    "int": _num,
    "float": _num,
    "str": _text,
    "color": _color,
    "choice": _choice,
    "path": _path,
}


def build_field(parent, spec, value, ctx):
    """按 spec['kind'] 构建控件，返回 (widget, tk_var)。"""
    kind = spec.get("kind", "str")
    builder = BUILDERS.get(kind)
    if builder is None:
        logger.warning("未知字段类型 %r，按文本处理", kind)
        builder = _text
    return builder(parent, spec, value, ctx)


__all__ = ["coerce", "_coerce", "build_field", "BUILDERS"]
