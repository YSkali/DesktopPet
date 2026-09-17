# -*- coding: utf-8 -*-
"""pet.py 纯函数测试（无需 GUI）。

覆盖已内联到 pet.py 的屏幕边缘行为（原 edge.py 的 clamp_x / direction_after）。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktoppet.pet import _clamp_x, _direction_after  # noqa: E402


def test_clamp_inside_range():
    assert _clamp_x(100, 800, 128) == (100, None)
    assert _clamp_x(1, 800, 128) == (1, None)


def test_clamp_left_edge():
    assert _clamp_x(-5, 800, 128) == (0, "left")
    assert _clamp_x(0, 800, 128) == (0, "left")


def test_clamp_right_edge():
    max_x = 800 - 128
    assert _clamp_x(max_x + 3, 800, 128) == (max_x, "right")
    assert _clamp_x(max_x, 800, 128) == (max_x, "right")


def test_clamp_degenerate_screen():
    # 屏幕窄到不足以移动时，不应反复判定撞边
    assert _clamp_x(10, 100, 128) == (0, None)


def test_direction_after():
    assert _direction_after("left") == 1
    assert _direction_after("right") == -1


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-q"]))
