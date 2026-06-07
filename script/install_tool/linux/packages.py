"""Linux 专属：系统包管理器检测与安装。"""
from __future__ import annotations

import os
import shutil
import subprocess

from ..core.config import InstallError
from ..core.console import step

# name -> (安装命令, 刷新源命令或 None)
_PKG_MANAGERS = {
    "apt": (["apt-get", "install", "-y"], ["apt-get", "update"]),
    "dnf": (["dnf", "install", "-y"], None),
    "yum": (["yum", "install", "-y"], None),
    "pacman": (["pacman", "-S", "--noconfirm"], None),
    "zypper": (["zypper", "install", "-y"], None),
}


def detect_package_manager() -> str | None:
    """返回当前系统可用的包管理器名称，找不到返回 None。"""
    for name in _PKG_MANAGERS:
        if shutil.which(name):
            return name
    return None


def sudo_prefix() -> list[str]:
    """非 root 且存在 sudo 时返回 ['sudo']，否则返回空列表。"""
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        return []
    if shutil.which("sudo"):
        return ["sudo"]
    return []


def pkg_install(packages: list[str]) -> None:
    """用系统包管理器安装一组软件包。失败抛出 InstallError。"""
    mgr = detect_package_manager()
    if mgr is None:
        raise InstallError(
            "未检测到受支持的包管理器 (apt/dnf/yum/pacman/zypper)，请手动安装。"
        )
    install_cmd, refresh_cmd = _PKG_MANAGERS[mgr]
    sudo = sudo_prefix()

    if refresh_cmd:
        step(f"刷新 {mgr} 软件源...")
        subprocess.run(sudo + refresh_cmd)

    step(f"使用 {mgr} 安装: {' '.join(packages)}")
    proc = subprocess.run(sudo + install_cmd + packages)
    if proc.returncode != 0:
        raise InstallError(f"{mgr} 安装失败 (退出码 {proc.returncode}): {' '.join(packages)}")
