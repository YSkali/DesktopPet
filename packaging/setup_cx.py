# -*- coding: utf-8 -*-
"""cx_Freeze 打包配置。

请在项目根目录执行（build.bat 已自动切换目录）::

    python packaging/setup_cx.py build
"""

import os
import sys

from cx_Freeze import Executable, setup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets_processed")
PETS = os.path.join(ROOT, "pets")

build_exe_options = {
    "packages": ["tkinter", "PIL", "desktoppet", "desktoppet.ui", "desktoppet.ui.pages"],
    # 把处理好的素材一起打进包里
    "include_files": [
        item
        for item in (
            (ASSETS, "assets_processed") if os.path.isdir(ASSETS) else None,
            (PETS, "pets") if os.path.isdir(PETS) else None,
        )
        if item
    ],
    "excludes": [
        "unittest", "email", "html", "http", "xml", "pydoc",
        "test", "distutils", "lib2to3", "pdb", "doctest",
    ],
}

base = "gui" if sys.platform == "win32" else None

setup(
    name="DesktopPet",
    version="1.10.0",
    description="桌面宠物 / Desktop Pet",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            os.path.join(ROOT, "run.py"),
            base=base,
            target_name="DesktopPet.exe" if sys.platform == "win32" else "DesktopPet",
            icon=None,
        )
    ],
)
