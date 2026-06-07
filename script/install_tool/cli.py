"""高层 CLI：解析参数、按平台注册表执行安装。

本模块只依赖 core 抽象与 factory，不直接 import 任何平台实现，
从而满足依赖倒置：高层策略不耦合具体平台细节。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core.config import IS_LINUX, IS_WINDOWS, Config, InstallError
from .core.console import err, ok, step, warn
from .factory import get_registry


def build_config(args: argparse.Namespace) -> Config:
    cfg = Config()
    if args.dev_root:
        cfg.dev_root = Path(args.dev_root)
    if args.download_dir:
        cfg.download_dir = Path(args.download_dir)
    if args.proxy:
        cfg.proxy = args.proxy
    if args.arch:
        cfg.arch = args.arch
    cfg.keep_archive = args.keep_archive
    return cfg


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="install_tools",
        description="easy-dev 跨平台工具链统一安装 CLI (Windows + Linux)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("tools", nargs="*", help="要安装的工具 (用 --list 查看)")
    parser.add_argument("--all", action="store_true", help="安装常用工具集")
    parser.add_argument("--list", action="store_true", help="列出所有可安装工具后退出")
    parser.add_argument("--dev-root", help=r"安装根目录 (Windows 默认 E:\Dev；Linux 由包管理器决定)")
    parser.add_argument("--download-dir", help=r"下载目录 (Windows 默认 E:\Downloads)")
    parser.add_argument("--proxy", help="HTTP/HTTPS 代理，如 http://127.0.0.1:10808")
    parser.add_argument("--arch", help="llvm-mingw 架构 (x86_64/aarch64/i686/armv7)")
    parser.add_argument("--keep-archive", action="store_true", help="保留下载的压缩包/安装器")
    args = parser.parse_args(argv)

    if not (IS_WINDOWS or IS_LINUX):
        err(f"暂不支持当前平台: {sys.platform} (仅支持 Windows 与 Linux)。")
        return 1

    registry = get_registry()

    if args.list:
        print("可安装工具:")
        for name in registry.tools:
            tag = " (不含于 --all)" if name not in registry.all_order else ""
            print(f"  - {name}{tag}")
        return 0

    selected = list(args.tools)
    if args.all:
        selected = registry.all_order + [t for t in selected if t not in registry.all_order]
    if not selected:
        parser.print_help()
        return 1

    unknown = [t for t in selected if t not in registry.tools]
    if unknown:
        err(f"未知工具: {', '.join(unknown)}。可用: {', '.join(registry.tools)}")
        return 1

    cfg = build_config(args)
    failures: list[str] = []
    for name in selected:
        print()
        step(f"=== 安装 {name} ===")
        try:
            registry.tools[name](cfg)
            ok(f"{name} 处理完成。")
        except InstallError as e:
            err(f"{name} 安装失败: {e}")
            failures.append(name)
        except Exception as e:  # noqa: BLE001 - 顶层兜底，单个工具失败不影响其余
            err(f"{name} 安装出现意外错误: {e}")
            failures.append(name)

    print()
    if failures:
        err(f"以下工具安装失败: {', '.join(failures)}")
        warn("提示：部分 PATH 变更需重启终端后生效，可重新运行 check_env.py 验证。")
        return 1
    ok("全部完成！部分 PATH 变更需重启终端后生效，可运行 check_env.py 验证。")
    return 0
