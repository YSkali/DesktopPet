# -*- coding: utf-8 -*-
"""工具页面：打开配置/目录，导入导出配置。"""

import os
import shutil
import tkinter as tk
from tkinter import filedialog

from ..._paths import app_dir, open_path
from .. import theme
from ..registry import Page, register


@register
class ToolsPage(Page):
    id = "tools"
    title = "工具"
    order = 60

    def build(self, parent, ctx):
        self.ctx = ctx
        theme.label(parent, "系统与维护", font=theme.FONT_BOLD,
                    anchor="w").pack(fill="x", padx=16, pady=(14, 6))
        theme.label(parent, "打开配置与目录、导入导出设置。导入后会自动应用；"
                            "其他页修改后记得「保存并应用」。",
                    fg=theme.SUB, font=theme.FONT_SMALL, anchor="w",
                    justify="left", wraplength=480).pack(
            fill="x", padx=16, pady=(0, 10))

        rows = (
            ("📄 打开配置文件", self._open_config),
            ("📁 打开程序目录", self._open_app_dir),
            ("🖼 打开角色包目录", self._open_pets_dir),
            ("📤 导出配置…", self._export_config),
            ("📥 导入配置…", self._import_config),
        )
        for text, cmd in rows:
            theme.button(parent, text, cmd).pack(anchor="w", padx=16, pady=4)

        self._hint = theme.label(parent, "", fg=theme.SUB, font=theme.FONT_SMALL,
                                 anchor="w", justify="left", wraplength=480)
        self._hint.pack(fill="x", padx=16, pady=(12, 4))

    # ---------- 路径 ----------
    def _config_path(self):
        return (getattr(self.ctx, "config_path", None)
                or os.path.join(app_dir(), "config.json"))

    def _pets_path(self):
        p = self.ctx.get("pets_dir", "pets") or "pets"
        return p if os.path.isabs(p) else os.path.join(app_dir(), p)

    # ---------- 打开 ----------
    def _open_config(self):
        path = self._config_path()
        if not os.path.exists(path):
            self.ctx.save()
        self._open(path)

    def _open_app_dir(self):
        self._open(app_dir())

    def _open_pets_dir(self):
        self._open(self._pets_path())

    def _open(self, path):
        ok = open_path(path)
        self._feedback(f"已打开：{path}" if ok else f"无法打开：{path}", ok)

    # ---------- 导入导出 ----------
    def _export_config(self):
        src = self._config_path()
        if not os.path.exists(src):
            self.ctx.save()
        dest = filedialog.asksaveasfilename(
            title="导出配置", defaultextension=".json", initialfile="config.json",
            filetypes=[("JSON", "*.json"), ("所有文件", "*.*")])
        if not dest:
            return
        try:
            shutil.copyfile(src, dest)
            self._feedback(f"已导出到：{dest}", True)
        except OSError as e:
            self._feedback(f"导出失败：{e}", False)

    def _import_config(self):
        src = filedialog.askopenfilename(
            title="导入配置", filetypes=[("JSON", "*.json"), ("所有文件", "*.*")])
        if not src:
            return
        try:
            self.ctx.config.load_from(src)
        except Exception as e:  # noqa: BLE001
            self._feedback(f"导入失败：{e}", False)
            return
        saved = self.ctx.save()
        self.ctx.apply()
        self._feedback("已导入并应用（重开控制台可见全部数值）" if saved
                       else "已导入，但写入 config.json 失败", saved)

    def _feedback(self, text, ok=True):
        if self._hint is not None:
            self._hint.configure(text=text,
                                 fg=theme.OK_FG if ok else theme.ERR_FG)
        self.ctx.notify(text, ok=ok)
