# -*- coding: utf-8 -*-
"""系统感知与人格台词：根据时间、CPU、内存与电池调整桌宠的心情与行为，并提供互动台词。

以纯函数为主，便于测试；对 psutil 等可选依赖做优雅降级。
"""

import logging
import os
import random as _random
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Mood:
    """一种心情，附带对行为参数的缩放系数。"""

    name: str
    label: str
    move_scale: float = 1.0
    anim_scale: float = 1.0
    rest_scale: float = 1.0


NORMAL = Mood("normal", "一切正常～")
ENERGETIC = Mood("energetic", "早上好呀！", 1.2, 0.9, 0.7)
SLEEPY = Mood("sleepy", "好困…想睡觉了", 0.7, 1.5, 1.8)
BUSY = Mood("busy", "电脑好像有点忙…", 0.8, 1.2, 1.3)
TIRED = Mood("tired", "好累呀，歇一会儿…", 0.55, 1.5, 1.7)
# 低电量：慢一点、歇得多，提醒主人充电
LOW_BATTERY = Mood("low_battery", "电量不多了，记得充电哦～", 0.75, 1.3, 1.6)


def time_period(hour=None):
    """把小时映射为时段：morning / day / evening / night。"""
    if hour is None:
        hour = datetime.now().hour
    if 5 <= hour < 11:
        return "morning"
    if 11 <= hour < 17:
        return "day"
    if 17 <= hour < 22:
        return "evening"
    return "night"


def greeting_for(period):
    """按时段返回一句问候语。"""
    return {
        "morning": "早上好呀，新的一天开始啦！",
        "day": "你好呀～",
        "evening": "晚上好！",
        "night": "夜深了，早点休息哦～",
    }.get(period, "你好呀～")


def read_cpu_percent():
    """读取 CPU 使用率（0-100）。不可用则返回 None。

    优先使用 psutil；其次用 os.getloadavg 近似；都不可用返回 None。
    """
    try:
        import psutil  # type: ignore

        return float(psutil.cpu_percent(interval=None))
    except Exception:  # noqa: BLE001 - psutil 缺失/异常都应降级
        pass
    try:
        load = os.getloadavg()[0]
        cpus = os.cpu_count() or 1
        return min(100.0, max(0.0, load / cpus * 100.0))
    except (OSError, AttributeError):
        return None


def read_memory_percent():
    """读取内存占用百分比（0-100）。不可用则返回 None。"""
    try:
        import psutil  # type: ignore

        return float(psutil.virtual_memory().percent)
    except Exception:  # noqa: BLE001
        return None


def read_battery():
    """读取电池信息。

    返回 ``(电量百分比, 是否正在充电)``；无电池或不可用返回 None。
    """
    try:
        import psutil  # type: ignore

        battery = psutil.sensors_battery()
        if battery is None:
            return None
        return float(battery.percent), bool(battery.power_plugged)
    except Exception:  # noqa: BLE001
        return None


def compute_mood(period, cpu, memory=None, battery=None):
    """根据时段、CPU、内存与电池计算心情。

    优先级：高负载 > 低电量 > 时段。

    - ``cpu`` / ``memory``：百分比（0-100）或 None。
    - ``battery``：``(电量百分比, 是否充电)`` 或 None。
    """
    if cpu is not None and cpu >= 80:
        return TIRED
    if memory is not None and memory >= 90:
        return TIRED
    if cpu is not None and cpu >= 50:
        return BUSY
    if memory is not None and memory >= 80:
        return BUSY
    if battery is not None:
        percent, plugged = battery
        if not plugged and percent <= 20:
            return LOW_BATTERY
    if period == "night":
        return SLEEPY
    if period == "morning":
        return ENERGETIC
    return NORMAL


# ---------- 人格台词库（可自由增删） ----------
LINES = {
    "click": [
        "呀！", "别戳我啦～", "痒痒的～", "干嘛呀？",
        "我在这儿呢！", "嘿嘿～", "咕噜咕噜～", "讨厌啦～",
    ],
    "drag": [
        "要带我去哪呀？", "诶诶诶～", "飞起来啦！",
        "放我下来嘛～", "好晕哦…", "轻点轻点～",
    ],
    "pet": [
        "好舒服～", "再摸摸嘛～", "最喜欢你啦！",
        "呼噜呼噜～", "谢谢你陪着我～", "嘿嘿，好开心～",
    ],
    "chatter": [
        "今天也要开心哦～", "在忙什么呢？", "要不要歇一会儿？",
        "我一直在这儿陪着你～", "加油呀！", "有点想你了～",
        "窗外天气好吗？", "别太累啦～",
    ],
}

CATEGORIES = tuple(LINES)


def random_line(category, rng=None):
    """返回该情境下的一句随机台词；未知情境返回空字符串。"""
    lines = LINES.get(category)
    if not lines:
        return ""
    chooser = rng or _random
    return chooser.choice(lines)


__all__ = [
    "Mood",
    "time_period",
    "greeting_for",
    "read_cpu_percent",
    "read_memory_percent",
    "read_battery",
    "compute_mood",
    "random_line",
    "LINES",
    "NORMAL",
    "ENERGETIC",
    "SLEEPY",
    "BUSY",
    "TIRED",
    "LOW_BATTERY",
]
