# -*- coding: utf-8 -*-
"""桌面控制台（页面式功能扩展）的单元测试（无需 GUI）。"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktoppet.config import DEFAULTS, Config  # noqa: E402
from desktoppet.ui.registry import (  # noqa: E402
    Page,
    PageContext,
    load_pages,
    register,
)
from desktoppet.ui.widgets import ConfigPage  # noqa: E402


def test_pages_registered_and_unique():
    pages = load_pages()
    assert pages, "应至少注册一个页面"
    ids = [p.id for p in pages]
    assert len(ids) == len(set(ids)), "页面 id 必须唯一"


def test_pages_sorted_by_order():
    orders = [p.order for p in load_pages()]
    assert orders == sorted(orders)


def test_pages_have_title_and_build():
    for p in load_pages():
        assert getattr(p, "title", ""), f"{p.id} 缺少标题"
        assert hasattr(p, "build")


def test_config_page_fields_valid():
    # 每个 ConfigPage 的字段键都必须存在于 Config.DEFAULTS，且 kind 有对应构建器
    from desktoppet.ui.widgets.fields import BUILDERS

    for p in load_pages():
        for field in getattr(p, "fields", ()):
            assert field["key"] in DEFAULTS, f"{p.id}: 未知配置键 {field['key']}"
            assert field.get("kind", "str") in BUILDERS


def test_context_get_set_roundtrip(tmp_path):
    cfg = Config(path=str(tmp_path / "c.json"))
    ctx = PageContext(config=cfg)
    assert ctx.set("move_speed", 7) is True
    assert ctx.get("move_speed") == 7
    assert ctx.save() is True
    cfg2 = Config(path=str(tmp_path / "c.json"))
    assert cfg2.get("move_speed") == 7


def test_context_unknown_key_rejected(tmp_path):
    cfg = Config(path=str(tmp_path / "c.json"))
    ctx = PageContext(config=cfg)
    assert ctx.set("definitely_not_a_key", 1) is False


def test_context_without_pet_is_safe(tmp_path):
    ctx = PageContext(config=None)
    assert ctx.apply() is None
    assert ctx.say("hi") is None
    ctx.switch_pack(0)  # 不应抛异常


def test_register_rejects_empty_id():
    class Bad(Page):
        id = ""
        title = "x"

    try:
        register(Bad)
    except ValueError:
        pass
    else:
        raise AssertionError("缺少 id 应抛 ValueError")


def test_config_page_is_page_subclass():
    assert issubclass(ConfigPage, Page)


def test_context_notify_callback():
    seen = []
    ctx = PageContext(config=None, notify=lambda text, ok=True: seen.append((text, ok)))
    ctx.notify("hi", ok=True)
    ctx.notify("bad", ok=False)
    assert seen == [("hi", True), ("bad", False)]


def test_context_notify_swallows_errors():
    def boom(text, ok=True):
        raise RuntimeError("boom")

    ctx = PageContext(config=None, notify=boom)
    ctx.notify("x")  # 不应抛异常


def test_config_save_bad_path_returns_false(tmp_path):
    cfg = Config(path=str(tmp_path / "c.json"))
    blocker = tmp_path / "afile"
    blocker.write_text("x", encoding="utf-8")
    # 目标父目录其实是文件 → 无法创建目录，应返回 False 而非抛异常
    assert cfg.save(str(blocker / "sub" / "c.json")) is False


def test_coerce_types():
    from desktoppet.ui.widgets import _coerce

    assert _coerce("bool", 0, True) is False
    assert _coerce("bool", 1, False) is True
    assert _coerce("int", 3.9, 0) == 3
    assert _coerce("float", "0.5", 0.0) == 0.5
    assert _coerce("str", 5, "x") == 5


def test_field_builders_cover_all_kinds_used():
    from desktoppet.ui.widgets.fields import BUILDERS

    # 页面实际用到的 kind 都有构建器
    used = set()
    for p in load_pages():
        for field in getattr(p, "fields", ()):
            used.add(field.get("kind", "str"))
    assert used <= set(BUILDERS), f"缺少构建器: {used - set(BUILDERS)}"


def test_config_load_from_merges(tmp_path):
    import json

    cfg = Config(path=str(tmp_path / "c.json"))
    src = tmp_path / "src.json"
    src.write_text(json.dumps({"move_speed": 9, "unknown_key": 1}),
                   encoding="utf-8")
    cfg.load_from(str(src))
    assert cfg.get("move_speed") == 9
    assert cfg.get("pet_size") == DEFAULTS["pet_size"]  # 保留默认
    assert "unknown_key" not in cfg._data  # 忽略未知键


def test_opacity_in_defaults():
    assert "opacity" in DEFAULTS
    assert 0.0 < DEFAULTS["opacity"] <= 1.0


def test_paths_log_helpers():
    from desktoppet import _paths

    assert _paths.log_file().endswith("desktoppet.log")
    assert "logs" in _paths.log_dir()


def test_platform_open_path_missing():
    from desktoppet._paths import open_path

    assert open_path("") is False
    assert open_path("/no/such/path/xyz") in (True, False)  # 不应抛异常
