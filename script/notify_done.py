#!/usr/bin/env python3
"""Stop 钩子：在 Claude 完成一轮任务、停下来等待用户时，弹出系统通知并播放提示音。

由 hooks.json 的 Stop 事件调用。读取（并忽略）stdin 上的钩子负载，按操作系统用
无第三方依赖的方式做提醒；任何失败都静默吞掉，始终以退出码 0 返回，绝不阻塞或
中断 Claude 的会话。通知一律放到分离的子进程里弹出，使钩子本身立即返回。
"""
import base64
import shutil
import subprocess
import sys

TITLE = "Claude Code"
MESSAGE = "任务完成，等待你的下一步"

# 静默子进程的通用参数
_QUIET = {
    "stdin": subprocess.DEVNULL,
    "stdout": subprocess.DEVNULL,
    "stderr": subprocess.DEVNULL,
}


def notify_windows() -> None:
    # 提示音：内置 winsound，瞬时且非阻塞
    try:
        import winsound

        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except Exception:
        pass

    # 系统通知：分离一个隐藏的 PowerShell 进程弹气泡，钩子无需等待它消失
    ps = (
        "Add-Type -AssemblyName System.Windows.Forms;"
        "Add-Type -AssemblyName System.Drawing;"
        "$n = New-Object System.Windows.Forms.NotifyIcon;"
        "$n.Icon = [System.Drawing.SystemIcons]::Information;"
        "$n.Visible = $true;"
        f"$n.ShowBalloonTip(5000, '{TITLE}', '{MESSAGE}',"
        " [System.Windows.Forms.ToolTipIcon]::Info);"
        "Start-Sleep -Seconds 6; $n.Dispose()"
    )
    # 用 -EncodedCommand 传 UTF-16LE，避免中文在命令行编码上出问题
    encoded = base64.b64encode(ps.encode("utf-16-le")).decode("ascii")
    # DETACHED_PROCESS | CREATE_NO_WINDOW，避免闪现控制台窗口
    flags = 0x00000008 | 0x08000000
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-EncodedCommand", encoded],
            creationflags=flags,
            **_QUIET,
        )
    except Exception:
        pass


def notify_macos() -> None:
    script = (
        f'display notification "{MESSAGE}" with title "{TITLE}" sound name "Glass"'
    )
    try:
        subprocess.Popen(["osascript", "-e", script], **_QUIET)
    except Exception:
        pass


def notify_linux() -> None:
    # 系统通知
    if shutil.which("notify-send"):
        try:
            subprocess.Popen(["notify-send", TITLE, MESSAGE], **_QUIET)
        except Exception:
            pass

    # 提示音：按可用性逐一尝试，命中第一个就停
    candidates = [
        ("canberra-gtk-play", ["-i", "complete"]),
        ("paplay", ["/usr/share/sounds/freedesktop/stereo/complete.oga"]),
        ("aplay", ["/usr/share/sounds/alsa/Front_Center.wav"]),
    ]
    for player, args in candidates:
        if shutil.which(player):
            try:
                subprocess.Popen([player] + args, **_QUIET)
            except Exception:
                pass
            break


def main() -> None:
    # 消费掉 stdin 上的钩子负载（当前不需要其中字段），避免管道异常
    try:
        sys.stdin.read()
    except Exception:
        pass

    try:
        if sys.platform == "win32":
            notify_windows()
        elif sys.platform == "darwin":
            notify_macos()
        else:
            notify_linux()
    except Exception:
        # 提醒失败绝不影响会话
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
