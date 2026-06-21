"""平台注册表抽象 —— 依赖倒置的核心接缝。

高层 CLI 与各平台的低层实现都依赖此处定义的抽象 (PlatformRegistry / InstallerFn)，
而非彼此。factory 在运行时按平台提供具体的 PlatformRegistry 实例。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from .config import Config


class InstallerFn(Protocol):
    """安装函数契约：接收配置、执行安装、失败时抛 InstallError。"""

    def __call__(self, cfg: Config) -> None: ...


@dataclass(frozen=True)
class PlatformRegistry:
    """某一平台暴露的能力集合。

    tools / updaters / uninstallers: 工具名 -> 对应操作的函数；三者键集合必须一致，
        即每个注册的工具都同时具备安装、更新、卸载三种能力。
    all_order:  `--all` 时按此顺序安装的工具子集 (排除依赖外部源的可选项)。
    """

    tools: dict[str, "Callable[[Config], None]"]
    updaters: dict[str, "Callable[[Config], None]"]
    uninstallers: dict[str, "Callable[[Config], None]"]
    all_order: list[str]

    def __post_init__(self) -> None:
        if self.tools.keys() != self.updaters.keys() or self.tools.keys() != self.uninstallers.keys():
            raise ValueError("tools / updaters / uninstallers 的工具键集合必须一致。")
