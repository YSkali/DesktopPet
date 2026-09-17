# -*- coding: utf-8 -*-
"""角色包系统的单元测试（无需 GUI）。"""

import json
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktoppet.packs import Pack, discover_packs, load_manifest  # noqa: E402


def _make_pack(root, name, states=("idle",), manifest=None):
    d = root / name
    for state in states:
        sd = d / state
        sd.mkdir(parents=True, exist_ok=True)
        Image.new("RGBA", (10, 10), (0, 0, 0, 0)).save(sd / "01.png")
    if manifest is not None:
        (d / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
        )
    return d


def test_discover_packs_sorted(tmp_path):
    _make_pack(tmp_path, "cat")
    _make_pack(tmp_path, "dog", states=("idle", "walk_left"))
    packs = discover_packs(str(tmp_path))
    assert [p.name for p in packs] == ["cat", "dog"]


def test_discover_skips_template_and_empty(tmp_path):
    _make_pack(tmp_path, "_template")
    (tmp_path / "empty").mkdir()
    assert discover_packs(str(tmp_path)) == []


def test_discover_missing_dir(tmp_path):
    assert discover_packs(str(tmp_path / "nope")) == []


def test_manifest_display_name_and_author(tmp_path):
    d = _make_pack(tmp_path, "cat", manifest={"name": "咪咪", "author": "me"})
    p = Pack("cat", str(d), load_manifest(str(d)))
    assert p.display_name == "咪咪"
    assert p.author == "me"


def test_load_manifest_broken_json(tmp_path):
    d = tmp_path / "bad"
    d.mkdir()
    (d / "manifest.json").write_text("{ not valid json", encoding="utf-8")
    assert load_manifest(str(d)) == {}


def test_available_states(tmp_path):
    d = _make_pack(tmp_path, "cat", states=("idle", "click"))
    p = Pack("cat", str(d))
    assert set(p.available_states()) == {"idle", "click"}
    assert not p.has_state("drag")
