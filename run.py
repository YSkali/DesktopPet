#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""桌宠启动入口（源码运行 / 打包入口）。

用法::

    python run.py
"""

import sys

from desktoppet.pet import main

if __name__ == "__main__":
    sys.exit(main())
