# -*- coding: utf-8 -*-
"""版本号测试（无需 GUI）。"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktoppet.version import __version__  # noqa: E402


def test_version_is_string():
    assert isinstance(__version__, str)
    assert __version__.count(".") == 2


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-q"]))
