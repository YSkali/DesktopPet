# -*- coding: utf-8 -*-
"""ConfigPage：由字段声明自动生成的配置页面。

子类只需声明 :attr:`fields`（及可选 :attr:`description`），即可获得
「读取当前配置 → 渲染控件 → 保存并落盘 → 请求即时生效」的完整能力。
覆盖 :meth:`get_fields` 可按运行期信息动态生成字段（如角色包下拉）。
"""

import tkinter as tk

from .. import theme
from ..registry import Page
from .fields import build_field, coerce


class ConfigPage(Page):
    fields = ()
    description = ""
    label_width = 14

    def get_fields(self, ctx):
        """返回字段列表；子类可覆盖以动态生成。"""
        return list(self.fields)

    # ---------- 构建 ----------
    def build(self, parent, ctx):
        self.ctx = ctx
        self._vars = {}
        self._hint = None
        if self.description:
            theme.label(parent, self.description, fg=theme.SUB,
                        font=theme.FONT_SMALL, justify="left", anchor="w",
                        wraplength=480).pack(fill="x", padx=16, pady=(14, 6))
        for spec in self.get_fields(ctx):
            self._build_row(parent, spec)
        self._build_bar(parent)

    def _build_row(self, parent, spec):
        row = theme.frame(parent)
        row.pack(fill="x", padx=16, pady=5)
        theme.label(row, spec.get("label", spec["key"]), width=self.label_width,
                    anchor="w").pack(side="left")
        widget, var = build_field(row, spec, self.ctx.get(spec["key"]), self.ctx)
        widget.pack(side="left")
        if spec.get("hint"):
            theme.label(row, spec["hint"], fg=theme.SUB, font=theme.FONT_SMALL,
                        anchor="w").pack(side="left", padx=8)
        self._vars[spec["key"]] = (spec, var)

    def _build_bar(self, parent):
        bar = theme.frame(parent)
        bar.pack(fill="x", padx=16, pady=14)
        theme.button(bar, "💾 保存并应用", self.apply, accent=True).pack(side="left")
        theme.button(bar, "↺ 恢复默认", self.restore_defaults).pack(side="left", padx=8)
        self._hint = theme.label(bar, "", fg=theme.SUB, font=theme.FONT_SMALL,
                                 anchor="w")
        self._hint.pack(side="left", padx=10)

    # ---------- 行为 ----------
    def collect(self):
        """返回 {key: 已类型转换的值}。"""
        out = {}
        for key, (spec, var) in self._vars.items():
            out[key] = coerce(spec.get("kind", "str"), var.get(),
                              self.ctx.get(key))
        return out

    def apply(self):
        """写回所有字段、落盘并即时生效，同时反馈结果。"""
        changed = 0
        for key, value in self.collect().items():
            if self.ctx.set(key, value):
                changed += 1
        saved = self.ctx.save()
        self.ctx.apply()
        if saved:
            msg = f"✓ 已保存并应用（{changed} 项）"
            self._flash(msg, ok=True)
            self.ctx.notify(msg, ok=True)
            self.ctx.say("设置已保存 ✨")
        else:
            msg = "⚠ 已应用，但写入 config.json 失败（重启后会丢失）"
            self._flash(msg, ok=False)
            self.ctx.notify("保存失败：无法写入 config.json", ok=False)
            self.ctx.say("保存失败了…")

    def restore_defaults(self):
        """把控件恢复为默认值（不落盘，需再点保存）。"""
        from ...config import DEFAULTS
        for key, (spec, var) in self._vars.items():
            default = DEFAULTS.get(key)
            kind = spec.get("kind", "str")
            if kind == "bool":
                var.set(1 if default else 0)
            elif kind in ("int", "float"):
                var.set(float(default if default is not None else 0))
            else:
                var.set("" if default is None else str(default))
        self._flash("已恢复默认值，点「保存并应用」后生效")

    def _flash(self, text, ok=True):
        if self._hint is not None:
            try:
                self._hint.configure(text=text,
                                     fg=theme.OK_FG if ok else theme.ERR_FG)
            except tk.TclError:
                pass


__all__ = ["ConfigPage"]
