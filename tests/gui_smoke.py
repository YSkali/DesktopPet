# -*- coding: utf-8 -*-
"""控制台 GUI 冒烟测试（需要图形界面，pytest 会自动忽略本文件）。

在真机上手动运行，验证「打开 → 逐页渲染 → 保存并应用 → 落盘」全链路：

    python tests/gui_smoke.py

它会自行弹出控制台窗口，检查每个页面都有内容，对配置页修改控件的值
并通过面板的保存入口（等价 Ctrl+S）写入临时 config.json，最后打印 PASS/FAIL。
"""

import json
import os
import sys
import tempfile
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktoppet.config import DEFAULTS, Config  # noqa: E402
from desktoppet.ui.panel import ControlPanel  # noqa: E402
from desktoppet.ui.widgets import ConfigPage  # noqa: E402


def walk(widget):
    yield widget
    for child in widget.winfo_children():
        yield from walk(child)


def main():
    root = tk.Tk()
    root.withdraw()
    cfg_path = os.path.join(tempfile.mkdtemp(), "config.json")
    cfg = Config(path=cfg_path)
    panel = ControlPanel(pet=None, config=cfg)
    win = panel.open()
    win.update_idletasks()

    ok = True
    print("页面:", [p.id for p in panel.pages])
    for i, pcls in enumerate(panel.pages):
        panel.select(i)
        win.update_idletasks()
        kids = panel._content.winfo_children()
        print(f"  页面 {pcls.id}: children={len(kids)}")
        if not kids:
            print(f"    !! {pcls.id} 页面为空")
            ok = False
            continue
        if issubclass(pcls, ConfigPage):
            widgets = list(walk(panel._content))
            for sc in [w for w in widgets if w.winfo_class() == "Scale"]:
                try:
                    sc.set(float(sc.cget("from")) + 1)
                except tk.TclError:
                    pass
            for cb in [w for w in widgets if w.winfo_class() == "Checkbutton"]:
                cb.invoke()
            panel.save_current()  # 等价 Ctrl+S / 标题栏保存
            win.update_idletasks()
            with open(cfg_path, encoding="utf-8") as f:
                disk = json.load(f)
            for key in DEFAULTS:
                assert key in disk, f"{pcls.id}: 缺少键 {key}"
            print(f"   保存 {pcls.id}: 已写盘 ({len(disk)} 键)")

    win.destroy()
    root.destroy()
    print("\n结果:", "PASS ✅" if ok else "FAIL ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
