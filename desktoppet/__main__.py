# -*- coding: utf-8 -*-
"""允许通过 ``python -m desktoppet`` 运行。"""

import sys

from .pet import main

if __name__ == "__main__":
    sys.exit(main())
