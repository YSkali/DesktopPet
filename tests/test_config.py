# -*- coding: utf-8 -*-
"""配置管理测试（无需 GUI）。"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktoppet.config import DEFAULTS, Config  # noqa: E402


def test_config_defaults_without_file(tmp_path):
    cfg = Config(path=str(tmp_path / "nope.json"))
    assert cfg.get("move_speed") == DEFAULTS["move_speed"]


def test_config_loads_and_ignores_unknown(tmp_path):
    p = tmp_path / "config.json"
    p.write_text(json.dumps({"move_speed": 9, "unknown_key": 1}), encoding="utf-8")
    cfg = Config(path=str(p))
    assert cfg.get("move_speed") == 9
    assert cfg.get("unknown_key") is None


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
