"""进程与命令执行的通用封装 (不含任何平台专属逻辑)。"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .config import InstallError
from .console import detail, warn


def which(cmd: str) -> str | None:
    return shutil.which(cmd)


def try_run(cmd: list[str]) -> None:
    """尝试运行验证命令，失败仅提醒不报错 (PATH 可能尚未在当前会话生效)。"""
    exe = which(cmd[0])
    if not exe:
        warn(f"当前会话尚未识别 '{cmd[0]}' 命令，可能需重启终端。")
        return
    try:
        subprocess.run([exe] + cmd[1:])
    except Exception as e:
        detail(f"验证命令执行异常: {e}")


def run_installer(installer: Path, args: list[str]) -> None:
    """运行安装器并等待结束；非零退出码抛出 InstallError。"""
    proc = subprocess.run([str(installer)] + args)
    if proc.returncode != 0:
        raise InstallError(f"安装器返回非零退出码 {proc.returncode}: {installer}")


def run_powershell(script: str) -> int:
    """执行一段 PowerShell 脚本 (用于 winget / 在线安装脚本等)。"""
    return subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script]
    ).returncode


def run_shell(script: str) -> int:
    """通过 bash 执行一段 shell 脚本 (Linux 上的在线安装脚本等)。"""
    return subprocess.run(["bash", "-lc", script]).returncode
