# -*- coding: utf-8 -*-
"""对话气泡：在桌宠上方显示一小段文字。

窗口在首次显示时才创建（懒加载），
任何异常都不应影响主程序（失败仅记录日志）。
"""

import logging
import tkinter as tk

logger = logging.getLogger(__name__)


class Bubble:
    """一个跟随在桌宠上方的简单文字气泡。"""

    def __init__(self, root, pet_size=128):
        self.root = root
        self.pet_size = pet_size
        self._win = None
        self._label = None
        self._after_id = None

    def _ensure(self):
        if self._win is not None:
            return
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        try:
            win.attributes("-topmost", True)
        except tk.TclError:
            pass
        frame = tk.Frame(win, bg="#2d2d2d", bd=1, relief="solid")
        frame.pack()
        label = tk.Label(
            frame,
            text="",
            bg="#2d2d2d",
            fg="white",
            font=("Microsoft YaHei", 10),
            padx=10,
            pady=6,
            justify="left",
            wraplength=220,
        )
        label.pack()
        self._win = win
        self._label = label

    def show(self, text, duration_ms=3500):
        """显示一段文字，duration_ms 后自动隐藏。"""
        if not text:
            return
        try:
            self._ensure()
            if self._after_id is not None:
                self.root.after_cancel(self._after_id)
            self._label.config(text=text)
            self._win.deiconify()
            self._position()
            self._win.lift()
            self._after_id = self.root.after(duration_ms, self.hide)
        except tk.TclError as e:
            logger.debug("气泡显示失败: %s", e)

    def _position(self):
        """把气泡放在桌宠上方（放不下则放到下方）。"""
        self._win.update_idletasks()
        w = self._win.winfo_width()
        h = self._win.winfo_height()
        x = self.root.winfo_x() + self.pet_size // 2 - w // 2
        y = self.root.winfo_y() - h - 4
        if y < 0:
            y = self.root.winfo_y() + self.pet_size + 4
        x = max(0, x)
        self._win.geometry(f"+{x}+{y}")

    def hide(self):
        self._after_id = None
        if self._win is not None:
            try:
                self._win.withdraw()
            except tk.TclError:
                pass


__all__ = ["Bubble"]
