"""Windows 具体安装实现：下载官方压缩包/安装器，部署并写入用户 PATH。

模块末尾导出 REGISTRY (PlatformRegistry)，由 factory 在 Windows 上选用。
"""
from __future__ import annotations

from pathlib import Path

from ..core import archive, net, proc
from ..core.base import PlatformRegistry
from ..core.config import Config, InstallError
from ..core.console import ok, print_summary, step, warn
from ..core.gittemplate import configure_git_template
from . import env


def install_cmake(cfg: Config, version: str = "4.3.2") -> None:
    install_path = cfg.dev_root / f"CMake-{version}"
    bin_path = install_path / "bin"
    exe = bin_path / "cmake.exe"
    if exe.exists():
        warn(f"CMake {version} 已安装于: {install_path}，跳过。")
    else:
        cfg.ensure_dirs()
        url = (
            f"https://github.com/Kitware/CMake/releases/download/v{version}/"
            f"cmake-{version}-windows-x86_64.zip"
        )
        step(f"\n下载并解压 CMake {version}...")
        a = net.download(url, cfg.download_dir / f"cmake-{version}.zip", cfg.proxy)
        archive.extract_zip_flatten(a, install_path)
        if not cfg.keep_archive:
            a.unlink(missing_ok=True)
        ok("CMake 部署成功!")
    env.path_msg(env.add_to_user_path(bin_path), "CMake")
    print_summary("CMAKE INSTALL SUMMARY", {
        "Version": version, "Install Dir": str(install_path),
        "Executable": str(exe), "Added to PATH": str(bin_path),
    })


def install_llvm(cfg: Config, msvcrt: str = "ucrt") -> None:
    step("\n从 GitHub API 获取 llvm-mingw 最新版本信息...")
    try:
        rel = net.github_latest("mstorsjo/llvm-mingw", cfg.proxy)
        version = rel["tag_name"]
        fname = f"llvm-mingw-{version}-{msvcrt}-{cfg.arch}.zip"
        asset = next((x for x in rel["assets"] if x["name"] == fname), None)
        if asset is None:
            raise InstallError(f"未找到匹配的发行资产: {fname}")
        url = asset["browser_download_url"]
    except InstallError:
        raise
    except Exception as e:
        raise InstallError(f"获取 llvm-mingw 最新版本失败: {e}") from e

    install_path = cfg.dev_root / f"llvm-mingw-{version}"
    bin_path = install_path / "bin"
    exe = bin_path / "clang.exe"
    if exe.exists():
        warn(f"llvm-mingw {version} 已安装于: {install_path}，跳过。")
    else:
        cfg.ensure_dirs()
        step(f"\n下载并解压 llvm-mingw {version} ({msvcrt}/{cfg.arch})...")
        a = net.download(url, cfg.download_dir / fname, cfg.proxy)
        archive.extract_zip_flatten(a, install_path)
        if not cfg.keep_archive:
            a.unlink(missing_ok=True)
        ok("llvm-mingw 部署成功!")
    env.path_msg(env.add_to_user_path(bin_path), "llvm-mingw")
    print_summary("LLVM-MINGW INSTALL SUMMARY", {
        "Version": f"{version} ({msvcrt}/{cfg.arch})", "Install Dir": str(install_path),
        "Executable": str(exe), "Added to PATH": str(bin_path),
    })
    proc.try_run(["clang", "--version"])


def install_git(cfg: Config, version: str = "2.54.0", arch: str = "64-bit") -> None:
    install_path = cfg.dev_root / f"MinGit-{version}"
    cmd_path = install_path / "cmd"
    exe = cmd_path / "git.exe"
    if exe.exists():
        warn(f"MinGit {version} 已安装于: {install_path}，跳过。")
    else:
        cfg.ensure_dirs()
        url = (
            f"https://github.com/git-for-windows/git/releases/download/"
            f"v{version}.windows.1/MinGit-{version}-{arch}.zip"
        )
        step(f"\n下载并解压 MinGit {version}...")
        a = net.download(url, cfg.download_dir / f"MinGit-{version}-{arch}.zip", cfg.proxy)
        archive.extract_zip_direct(a, install_path)
        if not cfg.keep_archive:
            a.unlink(missing_ok=True)
        ok("MinGit 部署成功!")
    env.path_msg(env.add_to_user_path(cmd_path), "MinGit")
    proc.try_run(["git", "--version"])
    configure_git_template()
    print_summary("MINGIT INSTALL SUMMARY", {
        "Version": f"{version} ({arch})", "Install Dir": str(install_path),
        "Executable": str(exe), "Added to PATH": str(cmd_path),
    })


def install_python(cfg: Config, version: str = "3.14.5") -> None:
    install_path = cfg.dev_root / "Python" / version
    exe = install_path / "python.exe"
    scripts = install_path / "Scripts"
    if exe.exists():
        warn(f"Python {version} 已安装于: {install_path}，跳过。")
    else:
        cfg.ensure_dirs()
        url = f"https://www.python.org/ftp/python/{version}/python-{version}-amd64.exe"
        step(f"\n下载并静默安装 Python {version}...")
        installer = net.download(url, cfg.download_dir / f"python-{version}-amd64.exe", cfg.proxy)
        proc.run_installer(installer, [
            "/quiet", "InstallAllUsers=0", "Include_test=0", f"TargetDir={install_path}",
        ])
        if not cfg.keep_archive:
            installer.unlink(missing_ok=True)
        ok("Python 安装成功!")
    c1 = env.add_to_user_path(install_path)
    c2 = env.add_to_user_path(scripts)
    env.path_msg(c1 or c2, "Python")
    print_summary("PYTHON INSTALL SUMMARY", {
        "Version": version, "Install Dir": str(install_path),
        "Executable": str(exe), "Added to PATH": f"{install_path}; {scripts}",
    })


def install_node(cfg: Config, version: str = "24.15.0") -> None:
    install_path = cfg.dev_root / f"Node-{version}"
    exe = install_path / "node.exe"
    if exe.exists():
        warn(f"Node.js {version} 已安装于: {install_path}，跳过。")
    else:
        cfg.ensure_dirs()
        url = f"https://nodejs.org/dist/v{version}/node-v{version}-win-x64.zip"
        step(f"\n下载并解压 Node.js {version}...")
        a = net.download(url, cfg.download_dir / f"node-v{version}.zip", cfg.proxy)
        archive.extract_zip_flatten(a, install_path)
        if not cfg.keep_archive:
            a.unlink(missing_ok=True)
        ok("Node.js 部署成功!")
    env.path_msg(env.add_to_user_path(install_path), "Node.js")
    warn("请重启终端以加载新的 node / npm 命令。")
    print_summary("NODEJS INSTALL SUMMARY", {
        "Version": version, "Install Dir": str(install_path),
        "Executable": str(exe), "Added to PATH": str(install_path),
    })


def install_vscode(cfg: Config) -> None:
    cfg.ensure_dirs()
    url = "https://update.code.visualstudio.com/latest/win32-x64/stable"
    step("\n下载并静默安装最新版 VS Code...")
    installer = net.download(url, cfg.download_dir / "VSCodeSetup-x64.exe", cfg.proxy)
    proc.run_installer(installer, ["/verysilent", "/mergetasks=desktopicon,addtopath"])
    if not cfg.keep_archive:
        installer.unlink(missing_ok=True)
    ok("VS Code 安装完成!")
    env.register_vscode_context_menu()


def install_claude(cfg: Config) -> None:
    """Claude CLI：官方在线安装脚本 (PowerShell)。"""
    step("\n执行 Claude 官方在线安装脚本...")
    proxy = cfg.proxy or ""
    prefix = f"$env:HTTP_PROXY='{proxy}'; $env:HTTPS_PROXY='{proxy}'; " if proxy else ""
    if proc.run_powershell(prefix + "irm https://claude.ai/install.ps1 | iex") != 0:
        raise InstallError("Claude 安装脚本执行失败。")
    claude_bin = Path.home() / ".local" / "bin"
    if claude_bin.exists():
        env.path_msg(env.add_to_user_path(claude_bin), "Claude")
    proc.try_run(["claude", "--version"])


def install_ccswith(cfg: Config) -> None:
    """ccswith：从 GitHub release 拉取最新版 Windows 资产，解压并加入 PATH。"""
    # TODO(setup): 替换为真实仓库 owner/repo 与资产命名规则（见 install_omposh 风格）。
    repo = "TODO/ccswith"
    step(f"\n从 GitHub API 获取 {repo} 最新 release...")
    try:
        rel = net.github_latest(repo, cfg.proxy)
        version = rel["tag_name"]
        # TODO(setup): 按真实资产名调整（占位：ccswith-{version}-windows-x86_64.zip）
        asset_name = f"ccswith-{version}-windows-x86_64.zip"
        asset = next((x for x in rel["assets"] if x["name"] == asset_name), None)
        if asset is None:
            raise InstallError(f"未找到匹配的发行资产: {asset_name}")
        url = asset["browser_download_url"]
    except InstallError:
        raise
    except Exception as e:
        raise InstallError(f"获取 {repo} 最新 release 失败: {e}") from e

    install_path = cfg.dev_root / f"ccswith-{version}"
    bin_path = install_path / "bin"
    # TODO(setup): 按真实可执行文件名调整（占位：ccswith.exe）
    exe = bin_path / "ccswith.exe"
    if exe.exists():
        warn(f"ccswith {version} 已安装于: {install_path}，跳过。")
    else:
        cfg.ensure_dirs()
        step(f"\n下载并解压 ccswith {version}...")
        a = net.download(url, cfg.download_dir / asset_name, cfg.proxy)
        archive.extract_zip_flatten(a, install_path)
        if not cfg.keep_archive:
            a.unlink(missing_ok=True)
        ok("ccswith 部署成功!")
    env.path_msg(env.add_to_user_path(bin_path), "ccswith")
    proc.try_run(["ccswith", "--version"])
    print_summary("CCSWITH INSTALL SUMMARY", {
        "Version": version, "Install Dir": str(install_path),
        "Executable": str(exe), "Added to PATH": str(bin_path),
    })


def install_omposh(cfg: Config) -> None:
    """Oh My Posh：通过 winget 安装并装 Cascadia Mono 字体。"""
    step("\n通过 winget 安装 Oh My Posh...")
    proxy = cfg.proxy or ""
    prefix = f"$env:HTTP_PROXY='{proxy}'; $env:HTTPS_PROXY='{proxy}'; " if proxy else ""
    script = prefix + (
        "winget install JanDeDobbeleer.OhMyPosh -s winget --silent "
        "--accept-source-agreements --accept-package-agreements; "
        "if (Get-Command oh-my-posh -ErrorAction SilentlyContinue) "
        "{ oh-my-posh font install cascadiamono }"
    )
    if proc.run_powershell(script) != 0:
        warn("Oh My Posh 安装可能未完全成功，请检查 winget 与网络。")
    else:
        ok("Oh My Posh 安装完成。请将终端字体改为 'CaskaydiaCove Nerd Font'。")


REGISTRY = PlatformRegistry(
    tools={
        "cmake": install_cmake,
        "llvm": install_llvm,
        "git": install_git,
        "python": install_python,
        "vscode": install_vscode,
        "node": install_node,
        "claude": install_claude,
        "omposh": install_omposh,
        "ccswith": install_ccswith,
    },
    all_order=["git", "cmake", "python", "vscode", "llvm", "node"],
)
