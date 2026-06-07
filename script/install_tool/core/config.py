"""安装行为的全局配置与统一异常类型。"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

IS_WINDOWS = sys.platform == "win32"
IS_LINUX = sys.platform.startswith("linux")


class InstallError(Exception):
    """安装过程中的可预期失败 (下载/解压/安装出错)。"""


def _default_dev_root() -> Path:
    return Path(r"E:\Dev") if IS_WINDOWS else Path.home() / "dev"


def _default_download_dir() -> Path:
    return Path(r"E:\Downloads") if IS_WINDOWS else Path.home() / "Downloads"


@dataclass
class Config:
    """安装行为的全局配置；默认值随平台变化，可经 CLI 覆盖。"""

    dev_root: Path = field(default_factory=_default_dev_root)
    download_dir: Path = field(default_factory=_default_download_dir)
    proxy: str | None = None          # 形如 "http://127.0.0.1:10808"；None 表示直连
    arch: str = "x86_64"              # llvm-mingw 用：x86_64 / aarch64 / i686 / armv7
    keep_archive: bool = False        # 安装后是否保留下载的压缩包/安装器

    def ensure_dirs(self) -> None:
        self.dev_root.mkdir(parents=True, exist_ok=True)
        self.download_dir.mkdir(parents=True, exist_ok=True)
