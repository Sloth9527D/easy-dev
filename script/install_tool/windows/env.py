"""Windows 专属：用户级 PATH 写入 (winreg) 与 VS Code 右键菜单注册。"""
from __future__ import annotations

import ctypes
import os
import winreg
from pathlib import Path

from ..core.console import err, ok, step


def add_to_user_path(new_dir: str | Path, prepend: bool = True) -> bool:
    """将 new_dir 加入当前用户 (HKCU) 的 PATH。已存在则不重复添加。

    返回 True 表示发生了修改。修改后广播 WM_SETTINGCHANGE 通知系统刷新。
    """
    new_dir = str(new_dir)
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, "Environment", 0,
        winreg.KEY_READ | winreg.KEY_WRITE,
    )
    try:
        try:
            current, _ = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            current = ""

        parts = [p for p in current.split(";") if p]
        if any(os.path.normcase(p) == os.path.normcase(new_dir) for p in parts):
            return False

        parts = [new_dir] + parts if prepend else parts + [new_dir]
        new_value = ";".join(parts)
        # 含 %VAR% 的路径需用 REG_EXPAND_SZ，避免破坏既有可展开变量
        write_type = winreg.REG_EXPAND_SZ if "%" in new_value else winreg.REG_SZ
        winreg.SetValueEx(key, "Path", 0, write_type, new_value)
    finally:
        winreg.CloseKey(key)

    _broadcast_env_change()
    os.environ["PATH"] = new_dir + os.pathsep + os.environ.get("PATH", "")
    return True


def path_msg(changed: bool, name: str) -> None:
    if changed:
        ok(f"已将 {name} 添加到用户 PATH。")
    else:
        ok(f"{name} 已在用户 PATH 中。")


def _broadcast_env_change() -> None:
    """广播 WM_SETTINGCHANGE，通知资源管理器等刷新环境变量。"""
    try:
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_ABORTIFHUNG = 0x0002
        result = ctypes.c_long()
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment",
            SMTO_ABORTIFHUNG, 5000, ctypes.byref(result),
        )
    except Exception:
        pass


def register_vscode_context_menu() -> None:
    """为 VS Code 注册 HKCU 右键菜单 (文件 / 文件夹 / 文件夹空白处)。"""
    step("\n注册 VS Code 右键菜单...")
    candidates = [
        r"C:\Program Files\Microsoft VS Code\Code.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
    ]
    code_exe = next((p for p in candidates if os.path.exists(p)), None)
    if not code_exe:
        err("未找到 Code.exe，跳过右键菜单注册。")
        return

    entries = [
        (r"Software\Classes\*\shell\VSCode", f'"{code_exe}" "%1"'),
        (r"Software\Classes\Directory\shell\VSCode", f'"{code_exe}" "%1"'),
        (r"Software\Classes\Directory\Background\shell\VSCode", f'"{code_exe}" "%V"'),
    ]
    try:
        for base, command in entries:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, base) as k:
                winreg.SetValueEx(k, None, 0, winreg.REG_SZ, "Open with Code")
                winreg.SetValueEx(k, "Icon", 0, winreg.REG_SZ, code_exe)
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, base + r"\command") as k:
                winreg.SetValueEx(k, None, 0, winreg.REG_SZ, command)
        ok("右键菜单注册成功!")
    except Exception as e:
        err(f"右键菜单注册失败: {e}")
