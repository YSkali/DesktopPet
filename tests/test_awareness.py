# -*- coding: utf-8 -*-
"""系统感知与人格台词的单元测试（无需 GUI）。"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktoppet.awareness import (  # noqa: E402
    BUSY,
    CATEGORIES,
    ENERGETIC,
    LINES,
    LOW_BATTERY,
    NORMAL,
    SLEEPY,
    TIRED,
    compute_mood,
    greeting_for,
    random_line,
    read_battery,
    read_cpu_percent,
    read_memory_percent,
    time_period,
)


# ---------- 心情 ----------

def test_time_period_boundaries():
    assert time_period(5) == "morning"
    assert time_period(10) == "morning"
    assert time_period(11) == "day"
    assert time_period(16) == "day"
    assert time_period(17) == "evening"
    assert time_period(21) == "evening"
    assert time_period(22) == "night"
    assert time_period(2) == "night"
    assert time_period(4) == "night"


def test_high_cpu_has_priority_over_period():
    assert compute_mood("morning", 90) is TIRED
    assert compute_mood("night", 90) is TIRED


def test_busy_range():
    assert compute_mood("day", 60) is BUSY
    assert compute_mood("day", 50) is BUSY


def test_mood_by_period_when_cpu_low():
    assert compute_mood("night", 10) is SLEEPY
    assert compute_mood("morning", 10) is ENERGETIC
    assert compute_mood("day", 10) is NORMAL
    assert compute_mood("evening", 10) is NORMAL


def test_cpu_none_is_handled():
    assert compute_mood("evening", None) is NORMAL
    assert compute_mood("night", None) is SLEEPY


def test_greeting_non_empty():
    for period in ("morning", "day", "evening", "night", "unknown"):
        text = greeting_for(period)
        assert isinstance(text, str) and text


def test_read_cpu_percent_type():
    value = read_cpu_percent()
    assert value is None or (0.0 <= value <= 100.0)


def test_memory_high_triggers_mood():
    assert compute_mood("day", 10, memory=95) is TIRED
    assert compute_mood("day", 10, memory=85) is BUSY


def test_low_battery_mood():
    assert compute_mood("day", 10, battery=(15, False)) is LOW_BATTERY
    # 充电中不算低电
    assert compute_mood("day", 10, battery=(15, True)) is NORMAL
    # 电量充足
    assert compute_mood("day", 10, battery=(80, False)) is NORMAL


def test_cpu_priority_over_battery():
    assert compute_mood("day", 90, battery=(10, False)) is TIRED


def test_memory_none_and_legacy_call():
    # 旧的两参数调用仍然可用，且 None 不误判
    assert compute_mood("day", 10) is NORMAL
    assert compute_mood("morning", 10) is ENERGETIC


def test_read_memory_and_battery_types():
    mem = read_memory_percent()
    assert mem is None or (0.0 <= mem <= 100.0)
    batt = read_battery()
    assert batt is None or (
        isinstance(batt, tuple)
        and len(batt) == 2
        and 0.0 <= batt[0] <= 100.0
        and isinstance(batt[1], bool)
    )


# ---------- 人格台词 ----------

def test_categories_have_lines():
    for category in CATEGORIES:
        assert LINES[category], f"{category} 台词库为空"


def test_random_line_returns_member():
    rng = random.Random(0)
    for _ in range(50):
        line = random_line("click", rng=rng)
        assert line in LINES["click"]


def test_random_line_unknown_category():
    assert random_line("not_a_category") == ""


def test_all_expected_categories_present():
    for name in ("click", "drag", "pet", "chatter"):
        assert name in LINES


def test_variety_at_least_three():
    for category in CATEGORIES:
        assert len(LINES[category]) >= 3


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-q"]))
