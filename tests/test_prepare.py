# -*- coding: utf-8 -*-
"""素材预处理测试（无需 GUI）。"""

import os
import sys

import pytest
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktoppet.prepare import (  # noqa: E402
    TARGET_SIZE,
    is_white_pixel,
    process_image,
    remove_background_floodfill,
)


def test_is_white_pixel():
    assert is_white_pixel((255, 255, 255, 255))
    assert not is_white_pixel((10, 10, 10, 255))


def test_remove_background_floodfill_edge_only():
    """四边相连的白色被清除，内部白色（眼睛）要保留。"""
    img = Image.new("RGBA", (10, 10), (255, 255, 255, 255))
    # 中心放一个黑色方块，方块内部再放一个白点（应保留）
    for x in range(3, 7):
        for y in range(3, 7):
            img.putpixel((x, y), (0, 0, 0, 255))
    img.putpixel((4, 4), (255, 255, 255, 255))

    out = remove_background_floodfill(img)
    assert out.getpixel((0, 0))[3] == 0        # 边缘白色 -> 透明
    assert out.getpixel((4, 4))[3] == 255      # 内部白点 -> 保留
    assert out.getpixel((3, 3))[3] == 255      # 黑色方块 -> 保留


def test_process_image_resizes(tmp_path):
    src = tmp_path / "src.png"
    dst = tmp_path / "out.png"
    Image.new("RGB", (500, 300), (255, 255, 255)).save(src)
    assert process_image(str(src), str(dst))
    with Image.open(dst) as out:
        assert out.size == TARGET_SIZE
        assert out.mode == "RGBA"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
