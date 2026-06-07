#!/usr/bin/env python3
"""easy-dev 工具链安装 CLI 启动器。

把 script/ 目录加入 sys.path 后调用 install_tool 包，使
`python script/install_tools.py ...` 能在任意工作目录下正常工作。
等价于 `python -m install_tool ...`(需在 script/ 目录内执行)。

用法:
    python script/install_tools.py --list
    python script/install_tools.py cmake llvm git
    python script/install_tools.py --all --proxy http://127.0.0.1:10808
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from install_tool.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
