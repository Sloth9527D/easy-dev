"""依赖倒置接缝：按当前平台惰性提供 PlatformRegistry。

CLI 只调用 get_registry()，永远不直接 import 任何平台实现模块；
因此 Windows 实现不会在 Linux 上被导入，反之亦然。
"""
from __future__ import annotations

import sys

from .core.base import PlatformRegistry
from .core.config import IS_LINUX, IS_WINDOWS


def get_registry() -> PlatformRegistry:
    """返回当前平台的安装注册表；不支持的平台抛 NotImplementedError。"""
    if IS_WINDOWS:
        from .windows.installers import REGISTRY
        return REGISTRY
    if IS_LINUX:
        from .linux.installers import REGISTRY
        return REGISTRY
    raise NotImplementedError(
        f"暂不支持当前平台: {sys.platform} (仅支持 Windows 与 Linux)。"
    )
