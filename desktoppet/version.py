# -*- coding: utf-8 -*-
"""版本号的唯一来源（single source of truth）。

发布新版本时只改这里的 __version__，
pyproject.toml 会动态读取它。
"""

__version__ = "1.10.0"

__all__ = ["__version__"]
