# -*- coding: utf-8 -*-
"""PageContext：页面与主程序之间的桥梁。

页面通过它读写配置、请求即时生效、让桌宠说话或切换角色包，
从而与 ``DesktopPet`` / ``Config`` 解耦，便于独立测试。
"""

import logging

logger = logging.getLogger(__name__)


class PageContext:
    def __init__(self, pet=None, config=None, notify=None):
        self.pet = pet
        self.config = config
        self._notify = notify

    # ---------- 配置 ----------
    @property
    def config_path(self):
        return getattr(self.config, "path", None)

    def get(self, key, default=None):
        if self.config is not None:
            value = self.config.get(key)
            return default if value is None else value
        return default

    def set(self, key, value):
        """写入一个配置项（不落盘）。返回是否成功。"""
        if self.config is not None:
            return bool(self.config.set(key, value))
        return False

    def save(self):
        """把配置写入 config.json。返回是否成功。"""
        if self.config is not None:
            return bool(self.config.save())
        return False

    # ---------- 状态反馈 ----------
    def notify(self, text, ok=True):
        """向控制台反馈一条状态信息（保存成功/失败等）。"""
        cb = self._notify
        if cb is not None:
            try:
                cb(text, ok)
            except Exception as e:  # noqa: BLE001
                logger.debug("状态反馈失败: %s", e)

    # ---------- 即时生效 ----------
    def apply(self):
        """请求主程序重新读取配置并即时生效。"""
        pet = self.pet
        if pet is not None and hasattr(pet, "apply_config"):
            try:
                pet.apply_config()
            except Exception as e:  # noqa: BLE001
                logger.warning("应用设置失败: %s", e)

    # ---------- 交互 ----------
    def say(self, text, duration_ms=2500):
        pet = self.pet
        if pet is not None and hasattr(pet, "say"):
            try:
                pet.say(text, duration_ms)
            except Exception as e:  # noqa: BLE001
                logger.debug("气泡提示失败: %s", e)

    def switch_pack(self, index):
        pet = self.pet
        if pet is not None and hasattr(pet, "switch_pack"):
            pet.switch_pack(index)


__all__ = ["PageContext"]
