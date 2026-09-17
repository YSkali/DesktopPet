# -*- coding: utf-8 -*-
"""路径工具：同时兼容“源码运行”和“打包后运行”。"""

import logging
import os
import sys

logger = logging.getLogger(__name__)


def app_dir():
    """返回应用根目录。

    - 打包后（cx_Freeze / PyInstaller）：exe 所在目录。
    - 源码运行：本项目根目录（desktoppet 包的上一级）。
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_path(*parts):
    """拼接应用根目录下的资源路径。"""
    return os.path.join(app_dir(), *parts)


def log_dir():
    """返回日志目录（不存在则创建）。"""
    d = os.path.join(app_dir(), "logs")
    try:
        os.makedirs(d, exist_ok=True)
    except OSError:
        pass
    return d


def log_file():
    """返回主日志文件路径。"""
    return os.path.join(log_dir(), "desktoppet.log")


def open_path(path):
    """用系统默认程序打开文件或目录。返回是否成功（不抛异常）。"""
    import subprocess

    try:
        if not path:
            return False
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception as e:  # noqa: BLE001
        logger.warning("打开路径失败 %s: %s", path, e)
        return False


__all__ = ["app_dir", "resource_path", "log_dir", "log_file", "open_path"]
