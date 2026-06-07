"""彩色终端输出 (对齐原 PowerShell 脚本的配色语义)。"""
from __future__ import annotations

import ctypes
import sys

from .config import IS_WINDOWS

_RESET = "\033[0m"
_COLORS = {
    "cyan": "\033[36m",      # 步骤标题
    "green": "\033[32m",     # 成功
    "yellow": "\033[33m",    # 提醒 / 跳过
    "red": "\033[31m",       # 错误
    "gray": "\033[90m",      # 次要细节
    "magenta": "\033[35m",   # 汇总框
}


def _enable_vt() -> None:
    """在 Windows 控制台启用 ANSI 转义序列 (VT 模式)；其它平台原生支持。"""
    if not IS_WINDOWS:
        return
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # VT processing
    except Exception:
        pass


_enable_vt()


def _c(text: str, color: str) -> str:
    return f"{_COLORS.get(color, '')}{text}{_RESET}"


def step(msg: str) -> None:
    print(_c(msg, "cyan"))


def ok(msg: str) -> None:
    print(_c(f"-> {msg}", "green"))


def warn(msg: str) -> None:
    print(_c(f"-> {msg}", "yellow"))


def err(msg: str) -> None:
    print(_c(f"-> {msg}", "red"))


def detail(msg: str) -> None:
    print(_c(f"   {msg}", "gray"))


def print_summary(title: str, rows: dict[str, str]) -> None:
    """打印对齐原脚本风格的安装信息汇总框。"""
    line = "=" * 50
    print()
    print(_c(line, "magenta"))
    print(_c(f"{title:^50}", "magenta"))
    print(_c(line, "magenta"))
    width = max((len(k) for k in rows), default=0)
    for k, v in rows.items():
        print(f" {k.ljust(width)} : {v}")
    print(_c(line, "magenta"))
