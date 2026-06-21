"""Windows 具体安装实现：下载官方压缩包/安装器，部署并写入用户 PATH。

模块末尾导出 REGISTRY (PlatformRegistry)，由 factory 在 Windows 上选用。
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from ..core import archive, net, proc
from ..core.base import PlatformRegistry
from ..core.config import Config, InstallError
from ..core.console import ok, print_summary, step, warn
from ..core.gittemplate import configure_git_template
from . import env


def _uninstall_versioned(cfg: Config, glob_pattern: str, path_subdirs: list[str], name: str) -> None:
    """卸载 dev_root 下匹配 glob_pattern 的所有版本目录，并清理对应的 PATH 项。

    path_subdirs 中的空字符串表示目录本身曾被加入 PATH (而非其某个子目录)。
    """
    matches = sorted(cfg.dev_root.glob(glob_pattern))
    if not matches:
        warn(f"未找到已安装的 {name}（{cfg.dev_root / glob_pattern}），跳过。")
        return
    for d in matches:
        for sub in path_subdirs:
            env.remove_from_user_path(d / sub if sub else d)
        shutil.rmtree(d, ignore_errors=True)
        ok(f"已删除: {d}")
    ok(f"{name} 卸载完成。")


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


def update_cmake(cfg: Config) -> None:
    step("\n从 GitHub API 获取 CMake 最新版本信息...")
    try:
        rel = net.github_latest("Kitware/CMake", cfg.proxy)
        version = rel["tag_name"].lstrip("v")
    except Exception as e:
        raise InstallError(f"获取 CMake 最新版本失败: {e}") from e
    uninstall_cmake(cfg)
    install_cmake(cfg, version=version)


def uninstall_cmake(cfg: Config) -> None:
    _uninstall_versioned(cfg, "CMake-*", ["bin"], "CMake")


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


def update_llvm(cfg: Config) -> None:
    uninstall_llvm(cfg)
    install_llvm(cfg)


def uninstall_llvm(cfg: Config) -> None:
    _uninstall_versioned(cfg, "llvm-mingw-*", ["bin"], "llvm-mingw")


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


def update_git(cfg: Config) -> None:
    step("\n从 GitHub API 获取 Git for Windows 最新版本信息...")
    try:
        rel = net.github_latest("git-for-windows/git", cfg.proxy)
        version = rel["tag_name"].lstrip("v").split(".windows.")[0]
    except Exception as e:
        raise InstallError(f"获取 Git for Windows 最新版本失败: {e}") from e
    uninstall_git(cfg)
    install_git(cfg, version=version)


def uninstall_git(cfg: Config) -> None:
    _uninstall_versioned(cfg, "MinGit-*", ["cmd"], "MinGit")


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


def update_python(cfg: Config) -> None:
    step("\n从 python.org 获取最新稳定版本信息...")
    try:
        version = net.latest_python_version(cfg.proxy)
    except Exception as e:
        raise InstallError(f"获取 Python 最新版本失败: {e}") from e
    uninstall_python(cfg)
    install_python(cfg, version=version)


def uninstall_python(cfg: Config) -> None:
    _uninstall_versioned(cfg, "Python/*", ["", "Scripts"], "Python")


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


def update_node(cfg: Config) -> None:
    step("\n从 nodejs.org 获取最新版本信息...")
    try:
        version = net.latest_node_version(cfg.proxy)
    except Exception as e:
        raise InstallError(f"获取 Node.js 最新版本失败: {e}") from e
    uninstall_node(cfg)
    install_node(cfg, version=version)


def uninstall_node(cfg: Config) -> None:
    _uninstall_versioned(cfg, "Node-*", [""], "Node.js")


def install_nvim(cfg: Config) -> None:
    """Neovim：从 GitHub release 拉取最新 Windows 资产 (nvim-win64.zip)，解压并加入 PATH。"""
    step("\n从 GitHub API 获取 Neovim 最新版本信息...")
    try:
        rel = net.github_latest("neovim/neovim", cfg.proxy)
        version = rel["tag_name"]
        asset = next((x for x in rel["assets"] if x["name"] == "nvim-win64.zip"), None)
        if asset is None:
            raise InstallError("未找到匹配的发行资产: nvim-win64.zip")
        url = asset["browser_download_url"]
    except InstallError:
        raise
    except Exception as e:
        raise InstallError(f"获取 Neovim 最新版本失败: {e}") from e

    install_path = cfg.dev_root / f"Neovim-{version}"
    bin_path = install_path / "bin"
    exe = bin_path / "nvim.exe"
    if exe.exists():
        warn(f"Neovim {version} 已安装于: {install_path}，跳过。")
    else:
        cfg.ensure_dirs()
        step(f"\n下载并解压 Neovim {version}...")
        a = net.download(url, cfg.download_dir / f"nvim-{version}-win64.zip", cfg.proxy)
        archive.extract_zip_flatten(a, install_path)
        if not cfg.keep_archive:
            a.unlink(missing_ok=True)
        ok("Neovim 部署成功!")
    env.path_msg(env.add_to_user_path(bin_path), "Neovim")
    proc.try_run(["nvim", "--version"])
    print_summary("NEOVIM INSTALL SUMMARY", {
        "Version": version, "Install Dir": str(install_path),
        "Executable": str(exe), "Added to PATH": str(bin_path),
    })


def update_nvim(cfg: Config) -> None:
    uninstall_nvim(cfg)
    install_nvim(cfg)


def uninstall_nvim(cfg: Config) -> None:
    _uninstall_versioned(cfg, "Neovim-*", ["bin"], "Neovim")


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


def update_vscode(cfg: Config) -> None:
    """VS Code 官方安装器本身即"覆盖安装最新版"，重新运行安装即可更新。"""
    install_vscode(cfg)


def uninstall_vscode(cfg: Config) -> None:
    candidates = [
        Path(r"C:\Program Files\Microsoft VS Code"),
        Path(os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code")),
    ]
    install_dir = next((p for p in candidates if (p / "unins000.exe").exists()), None)
    if not install_dir:
        warn("未找到 VS Code 安装目录，跳过卸载。")
        return
    step("\n运行 VS Code 卸载程序...")
    proc.run_installer(install_dir / "unins000.exe", ["/verysilent"])
    env.unregister_vscode_context_menu()
    ok("VS Code 卸载完成。")


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


def update_claude(cfg: Config) -> None:
    """官方安装脚本本身具备更新能力，重新执行即可。"""
    install_claude(cfg)


def uninstall_claude(cfg: Config) -> None:
    claude_bin = Path.home() / ".local" / "bin"
    removed = False
    for fname in ("claude.exe", "claude"):
        f = claude_bin / fname
        if f.exists():
            f.unlink()
            removed = True
    if removed:
        ok("已删除 Claude CLI 可执行文件。")
    else:
        warn(f"未在 {claude_bin} 找到 Claude CLI 可执行文件，可能安装位置不同，需手动检查。")
    warn("用户目录下的 Claude 配置/缓存（如 %USERPROFILE%\\.claude）未被清理，需要的话请手动删除。")


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


def update_ccswith(cfg: Config) -> None:
    uninstall_ccswith(cfg)
    install_ccswith(cfg)


def uninstall_ccswith(cfg: Config) -> None:
    _uninstall_versioned(cfg, "ccswith-*", ["bin"], "ccswith")


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


def update_omposh(cfg: Config) -> None:
    step("\n通过 winget 更新 Oh My Posh...")
    proxy = cfg.proxy or ""
    prefix = f"$env:HTTP_PROXY='{proxy}'; $env:HTTPS_PROXY='{proxy}'; " if proxy else ""
    script = prefix + (
        "winget upgrade JanDeDobbeleer.OhMyPosh --silent "
        "--accept-source-agreements --accept-package-agreements"
    )
    if proc.run_powershell(script) != 0:
        warn("Oh My Posh 更新可能未完全成功 (也可能已是最新版)，请检查 winget。")
    else:
        ok("Oh My Posh 更新完成。")


def uninstall_omposh(cfg: Config) -> None:
    step("\n通过 winget 卸载 Oh My Posh...")
    if proc.run_powershell("winget uninstall JanDeDobbeleer.OhMyPosh --silent") != 0:
        warn("Oh My Posh 卸载可能未完全成功，请检查 winget。")
    else:
        ok("Oh My Posh 卸载完成。")


REGISTRY = PlatformRegistry(
    tools={
        "cmake": install_cmake,
        "llvm": install_llvm,
        "git": install_git,
        "python": install_python,
        "vscode": install_vscode,
        "node": install_node,
        "nvim": install_nvim,
        "claude": install_claude,
        "omposh": install_omposh,
        "ccswith": install_ccswith,
    },
    updaters={
        "cmake": update_cmake,
        "llvm": update_llvm,
        "git": update_git,
        "python": update_python,
        "vscode": update_vscode,
        "node": update_node,
        "nvim": update_nvim,
        "claude": update_claude,
        "omposh": update_omposh,
        "ccswith": update_ccswith,
    },
    uninstallers={
        "cmake": uninstall_cmake,
        "llvm": uninstall_llvm,
        "git": uninstall_git,
        "python": uninstall_python,
        "vscode": uninstall_vscode,
        "node": uninstall_node,
        "nvim": uninstall_nvim,
        "claude": uninstall_claude,
        "omposh": uninstall_omposh,
        "ccswith": uninstall_ccswith,
    },
    all_order=["git", "cmake", "python", "vscode", "llvm", "node"],
)
