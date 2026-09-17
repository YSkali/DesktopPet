# -*- coding: utf-8 -*-
"""页面注册表：桌面控制台的功能扩展核心。

每个功能页面继承 :class:`Page`，用 ``@register`` 装饰器注册；控制台
（``panel.py``）打开时通过 :func:`load_pages` 自动发现并按 ``order``
排序。**加功能 = 在 ``ui/pages/`` 放一个新模块并注册**，控制台本体
无需任何改动。

注册表本身不创建任何窗口，可安全地在无显示环境（CI / 单元测试）中导入。
"""

import logging

from .context import PageContext  # noqa: F401  兼容旧导入路径

logger = logging.getLogger(__name__)


class Page:
    """一个控制台页面。

    子类至少覆盖 :attr:`id` / :attr:`title` 与 :meth:`build`。
    """

    id = ""
    title = ""
    order = 100
    icon = ""

    def build(self, parent, ctx):
        """在 ``parent``（tk 容器）里构建页面内容。"""
        raise NotImplementedError


_PAGES = []  # list[type[Page]]


def register(page_cls):
    """页面注册装饰器。重复 id 会被忽略并告警。"""
    if not getattr(page_cls, "id", ""):
        raise ValueError(f"页面 {page_cls!r} 缺少 id")
    if any(p.id == page_cls.id for p in _PAGES):
        logger.warning("重复的页面 id: %s（已忽略）", page_cls.id)
        return page_cls
    _PAGES.append(page_cls)
    return page_cls


def get_pages():
    """返回已注册的页面类，按 (order, title) 排序。"""
    return sorted(_PAGES, key=lambda p: (p.order, p.title))


def load_pages():
    """确保内置页面已导入，然后返回页面列表。"""
    from . import pages  # noqa: F401  —— 导入即触发各页面的注册
    return get_pages()


__all__ = ["Page", "PageContext", "register", "get_pages", "load_pages"]
