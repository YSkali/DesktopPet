# -*- coding: utf-8 -*-
"""桌面控制台（设置面板）：承载所有功能页面的 Tk 窗口。

- 左侧导航由页面注册表动态生成；右侧显示当前页面内容；
- 顶部标题栏：标题 + 状态反馈 + 「保存」(Ctrl+S) + 关闭；支持 Esc 关闭；
- 底部状态栏：版本、配置文件路径与快捷键提示；
- 打开时居中并短暂置顶，避免被置顶的桌宠遮挡；
- 单例：重复打开只会聚焦已有窗口。
"""

import logging
import tkinter as tk

from ..version import __version__
from . import theme
from .context import PageContext
from .registry import load_pages

logger = logging.getLogger(__name__)

DEFAULT_W, DEFAULT_H = 820, 580


class ControlPanel:
    """控制台窗口。每个桌宠实例持有一个即可。"""

    def __init__(self, pet=None, config=None):
        self.pet = pet
        self.config = config
        self.ctx = PageContext(pet=pet, config=config, notify=self.notify)
        self.pages = load_pages()
        self._win = None
        self._content = None
        self._nav = None
        self._nav_buttons = {}
        self._save_btn = None
        self._status = None
        self._status_job = None
        self._active = None
        self._current = None

    # ---------- 生命周期 ----------
    def open(self):
        """打开（或聚焦）控制台窗口。"""
        if self._win is not None:
            try:
                self._win.deiconify()
                self._win.lift()
                self._flash_topmost()
                self._win.focus_force()
                return self._win
            except tk.TclError:
                self._win = None

        root = getattr(self.pet, "root", None) or tk._default_root
        win = tk.Toplevel(root)
        self._win = win
        win.title(f"桌面宠物 · 控制台  v{__version__}")
        win.configure(bg=theme.BG)
        win.minsize(640, 460)
        self._center(win, DEFAULT_W, DEFAULT_H)
        try:
            win.transient(root)
        except tk.TclError:
            pass
        self._flash_topmost()
        win.protocol("WM_DELETE_WINDOW", self.close)
        win.bind("<Escape>", lambda _e: self.close())
        win.bind("<Control-s>", lambda _e: self.save_current())

        self._build_header(win)
        body = theme.frame(win)
        body.pack(fill="both", expand=True)
        self._build_nav(body)
        self._content = theme.frame(body)
        self._content.pack(side="left", fill="both", expand=True)
        self._build_footer(win)

        if self.pages:
            self.select(0)
        try:
            win.deiconify()
            win.lift()
            win.focus_force()
        except tk.TclError:
            pass
        return win

    def _build_header(self, win):
        header = theme.frame(win, bg=theme.HEADER_BG)
        header.pack(fill="x")
        theme.label(header, "🐾 桌面宠物 · 控制台", fg=theme.FG,
                    bg=theme.HEADER_BG, font=theme.FONT_TITLE).pack(
            side="left", padx=14, pady=10)
        theme.button(header, "✕ 关闭", self.close).pack(side="right", padx=10)
        self._save_btn = theme.button(header, "💾 保存 (Ctrl+S)", self.save_current)
        self._save_btn.pack(side="right")
        self._status = theme.label(header, "", fg=theme.SUB, bg=theme.HEADER_BG,
                                   font=theme.FONT_SMALL, anchor="e")
        self._status.pack(side="right", padx=10)

    def _build_nav(self, body):
        self._nav = theme.frame(body, bg=theme.NAV_BG, width=140)
        self._nav.pack(side="left", fill="y")
        self._nav.pack_propagate(False)
        for i, page_cls in enumerate(self.pages):
            btn = tk.Button(self._nav, text=f"  {page_cls.title}", anchor="w",
                            relief="flat", bd=0, padx=14, pady=9,
                            bg=theme.NAV_BG, fg=theme.FG,
                            activebackground=theme.ACCENT,
                            activeforeground=theme.ACCENT_FG, cursor="hand2",
                            command=lambda i=i: self.select(i))
            btn.pack(fill="x")
            self._nav_buttons[i] = btn

    def _build_footer(self, win):
        footer = theme.frame(win, bg=theme.FOOTER_BG)
        footer.pack(fill="x", side="bottom")
        cfg_path = str(getattr(self.config, "path", "") or "")
        theme.label(footer, f"v{__version__}   ·   配置：{cfg_path}",
                    fg=theme.SUB, bg=theme.FOOTER_BG, font=theme.FONT_SMALL,
                    anchor="w").pack(side="left", padx=14, pady=5)
        theme.label(footer, "Esc 关闭 · Ctrl+S 保存", fg=theme.SUB,
                    bg=theme.FOOTER_BG, font=theme.FONT_SMALL).pack(
            side="right", padx=14)

    # ---------- 窗口辅助 ----------
    def _center(self, win, w, h):
        try:
            sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
            x = max(0, (sw - w) // 2)
            y = max(0, (sh - h) // 3)
            win.geometry(f"{w}x{h}+{x}+{y}")
        except tk.TclError:
            win.geometry(f"{w}x{h}")

    def _flash_topmost(self):
        """打开/聚焦时短暂置顶，1.5 秒后取消（不影响桌宠自身置顶）。"""
        try:
            self._win.attributes("-topmost", True)
            self._win.after(1500, self._release_topmost)
        except tk.TclError:
            pass

    def _release_topmost(self):
        try:
            if self._win is not None and self._win.winfo_exists():
                self._win.attributes("-topmost", False)
        except tk.TclError:
            pass

    # ---------- 页面切换 ----------
    def select(self, index):
        """切到第 index 个页面。"""
        if not (0 <= index < len(self.pages)):
            return
        for i, btn in self._nav_buttons.items():
            btn.configure(bg=theme.ACCENT if i == index else theme.NAV_BG,
                          fg="white" if i == index else theme.FG)
        for child in self._content.winfo_children():
            child.destroy()
        page_cls = self.pages[index]
        try:
            page = page_cls()
            page.build(self._content, self.ctx)
            self._current = page
            if self._save_btn is not None:
                self._save_btn.configure(
                    state="normal" if hasattr(page, "apply") else "disabled")
        except Exception as e:  # noqa: BLE001
            logger.exception("页面 %s 构建失败", page_cls.id)
            self._current = None
            theme.label(self._content, justify="left", anchor="w",
                        fg=theme.ERR_FG, wraplength=460,
                        text=f"⚠ 页面加载失败：{page_cls.id}\n\n{e}").pack(
                padx=16, pady=16, fill="x")
            self.notify("页面加载失败", ok=False)
        self._active = index

    def save_current(self):
        """保存当前页面（由标题栏按钮 / Ctrl+S 触发）。"""
        page = self._current
        if page is not None and hasattr(page, "apply"):
            try:
                page.apply()
            except Exception as e:  # noqa: BLE001
                logger.exception("保存当前页失败")
                self.notify(f"保存失败：{e}", ok=False)
        else:
            self.notify("本页没有可保存的设置", ok=False)

    # ---------- 状态反馈 ----------
    def notify(self, text, ok=True):
        """在标题栏显示一条状态信息。"""
        if self._status is None:
            return
        try:
            self._status.configure(text=text,
                                   fg=theme.OK_FG if ok else theme.ERR_FG)
        except tk.TclError:
            return
        if self._status_job is not None:
            try:
                self._win.after_cancel(self._status_job)
            except (tk.TclError, ValueError):
                pass
        try:
            self._status_job = self._win.after(
                4000, lambda: self._status and self._status.configure(text=""))
        except tk.TclError:
            self._status_job = None

    def close(self):
        if self._win is not None:
            try:
                self._win.destroy()
            except tk.TclError:
                pass
        self._win = None
        self._content = None
        self._nav = None
        self._status = None
        self._save_btn = None
        self._current = None
        self._nav_buttons = {}


__all__ = ["ControlPanel"]
