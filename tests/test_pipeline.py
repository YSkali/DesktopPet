# -*- coding: utf-8 -*-
"""图片 -> 桌宠 流水线的单元测试（无需 GUI）。"""

import json
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktoppet.pipeline import (  # noqa: E402
    build_pet,
    classify_state,
    collect_images,
    detect_state,
)


def _white(path, size=(120, 120)):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.new("RGB", size, (255, 255, 255)).save(path)


# ---------- classify_state ----------

def test_classify_canonical():
    for state in ("idle", "walk_left", "click", "drag", "pet"):
        assert classify_state(state) == state


def test_classify_chinese_aliases():
    assert classify_state("待机") == "idle"
    assert classify_state("向左走") == "walk_left"
    assert classify_state("点击") == "click"
    assert classify_state("被拖拽") == "drag"
    assert classify_state("抚摸") == "pet"


def test_classify_filename_prefix():
    assert classify_state("idle_01") == "idle"
    assert classify_state("walk-02") == "walk_left"
    assert classify_state("click") == "click"


def test_classify_unknown():
    assert classify_state("01") is None
    assert classify_state("") is None
    assert classify_state("portrait") is None


# ---------- detect_state ----------

def test_detect_state_prefers_parent(tmp_path):
    p = tmp_path / "my_pet" / "idle" / "01.png"
    _white(str(p))
    assert detect_state(str(p)) == "idle"


def test_detect_state_from_filename(tmp_path):
    p = tmp_path / "my_pet" / "walk_01.png"
    _white(str(p))
    assert detect_state(str(p)) == "walk_left"


def test_detect_state_none(tmp_path):
    p = tmp_path / "my_pet" / "01.png"
    _white(str(p))
    assert detect_state(str(p)) is None


# ---------- collect_images ----------

def test_collect_images_recursive_sorted(tmp_path):
    _white(str(tmp_path / "b" / "2.png"))
    _white(str(tmp_path / "a" / "1.png"))
    files = collect_images(str(tmp_path))
    assert len(files) == 2
    assert files == sorted(files)


# ---------- build_pet ----------

def test_build_pet_structure(tmp_path):
    src = tmp_path / "upload" / "cat"
    _white(str(src / "idle" / "01.png"))
    _white(str(src / "idle" / "02.png"))
    _white(str(src / "click" / "01.png"))
    out = tmp_path / "pets"

    result = build_pet(str(src), "cat", out_dir=str(out),
                       display_name="咪咪", author="tester")

    assert result["states"]["idle"] == 2
    assert result["states"]["click"] == 1
    assert result["total"] == 3
    assert os.path.isfile(out / "cat" / "idle" / "01.png")
    manifest = json.loads((out / "cat" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "咪咪"
    assert manifest["author"] == "tester"


def test_build_pet_flat_prefix(tmp_path):
    src = tmp_path / "upload" / "dog"
    _white(str(src / "idle_01.png"))
    _white(str(src / "walk_01.png"))
    _white(str(src / "walk_02.png"))
    out = tmp_path / "pets"

    result = build_pet(str(src), "dog", out_dir=str(out))
    assert result["states"].get("idle") == 1
    assert result["states"].get("walk_left") == 2


def test_build_pet_defaults_to_idle(tmp_path):
    src = tmp_path / "upload" / "plain"
    _white(str(src / "01.png"))
    _white(str(src / "02.png"))
    out = tmp_path / "pets"

    result = build_pet(str(src), "plain", out_dir=str(out))
    assert result["states"] == {"idle": 2}


def test_build_pet_single_image(tmp_path):
    src = tmp_path / "upload" / "solo" / "only.png"
    _white(str(src))
    out = tmp_path / "pets"
    result = build_pet(str(tmp_path / "upload" / "solo"), "solo", out_dir=str(out))
    assert result["total"] == 1
    assert result["states"] == {"idle": 1}


def test_build_pet_no_images_raises(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    try:
        build_pet(str(empty), "x", out_dir=str(tmp_path / "pets"))
    except ValueError:
        pass
    else:
        raise AssertionError("空目录应抛出 ValueError")


def test_build_pet_resizes(tmp_path):
    src = tmp_path / "upload" / "big"
    _white(str(src / "idle_01.png"), size=(400, 400))
    out = tmp_path / "pets"
    build_pet(str(src), "big", out_dir=str(out))
    with Image.open(out / "big" / "idle" / "01.png") as im:
        assert im.size == (128, 128)
