"""Linux 具体安装实现：通过系统包管理器安装对应软件包。

模块末尾导出 REGISTRY (PlatformRegistry)，由 factory 在 Linux 上选用。
"""
from __future__ import annotations

import shutil
from pathlib import Path

from ..core import net, proc
from ..core.base import PlatformRegistry
from ..core.config import Config, InstallError
from ..core.console import ok, step, warn
from ..core.gittemplate import configure_git_template
from . import packages

# 工具 -> 各包管理器对应的包名 (default 适用于 apt/dnf/yum/zypper，pacman 单列差异)
_PACKAGES: dict[str, dict[str, list[str]]] = {
    "cmake": {"default": ["cmake"]},
    "llvm": {"default": ["clang"]},
    "git": {"default": ["git"]},
    "node": {"default": ["nodejs", "npm"]},
    "python": {"default": ["python3", "python3-pip"], "pacman": ["python", "python-pip"]},
    "nvim": {"default": ["neovim"]},
}


def _pkg(tool: str) -> None:
    mgr = packages.detect_package_manager()
    spec = _PACKAGES[tool]
    pkgs = spec.get(mgr, spec["default"]) if mgr else spec["default"]
    packages.pkg_install(pkgs)
    ok(f"{tool} 安装完成。")


def _pkg_remove(tool: str) -> None:
    mgr = packages.detect_package_manager()
    spec = _PACKAGES[tool]
    pkgs = spec.get(mgr, spec["default"]) if mgr else spec["default"]
    packages.pkg_remove(pkgs)
    ok(f"{tool} 卸载完成。")


def _pkg_upgrade(tool: str) -> None:
    mgr = packages.detect_package_manager()
    spec = _PACKAGES[tool]
    pkgs = spec.get(mgr, spec["default"]) if mgr else spec["default"]
    packages.pkg_upgrade(pkgs)
    ok(f"{tool} 更新完成。")


def install_cmake(cfg: Config) -> None:
    _pkg("cmake")
    proc.try_run(["cmake", "--version"])


def update_cmake(cfg: Config) -> None:
    _pkg_upgrade("cmake")
    proc.try_run(["cmake", "--version"])


def uninstall_cmake(cfg: Config) -> None:
    _pkg_remove("cmake")


def install_llvm(cfg: Config) -> None:
    _pkg("llvm")
    proc.try_run(["clang", "--version"])


def update_llvm(cfg: Config) -> None:
    _pkg_upgrade("llvm")
    proc.try_run(["clang", "--version"])


def uninstall_llvm(cfg: Config) -> None:
    _pkg_remove("llvm")


def install_git(cfg: Config) -> None:
    _pkg("git")
    proc.try_run(["git", "--version"])
    configure_git_template()


def update_git(cfg: Config) -> None:
    _pkg_upgrade("git")
    proc.try_run(["git", "--version"])


def uninstall_git(cfg: Config) -> None:
    _pkg_remove("git")


def install_python(cfg: Config) -> None:
    _pkg("python")
    proc.try_run(["python3", "--version"])


def update_python(cfg: Config) -> None:
    _pkg_upgrade("python")
    proc.try_run(["python3", "--version"])


def uninstall_python(cfg: Config) -> None:
    _pkg_remove("python")


def install_node(cfg: Config) -> None:
    _pkg("node")
    proc.try_run(["node", "--version"])


def update_node(cfg: Config) -> None:
    _pkg_upgrade("node")
    proc.try_run(["node", "--version"])


def uninstall_node(cfg: Config) -> None:
    _pkg_remove("node")


def install_nvim(cfg: Config) -> None:
    _pkg("nvim")
    proc.try_run(["nvim", "--version"])


def update_nvim(cfg: Config) -> None:
    _pkg_upgrade("nvim")
    proc.try_run(["nvim", "--version"])


def uninstall_nvim(cfg: Config) -> None:
    _pkg_remove("nvim")


def install_vscode(cfg: Config) -> None:
    """VS Code 不在多数发行版默认源中：优先 snap，其次提示官方安装方式。"""
    if proc.which("code"):
        warn("VS Code (code) 已安装，跳过。")
        return
    if proc.which("snap"):
        cmd = " ".join(packages.sudo_prefix() + ["snap", "install", "code", "--classic"])
        if proc.run_shell(cmd) != 0:
            raise InstallError("snap 安装 VS Code 失败。")
        ok("VS Code 安装完成!")
        return
    raise InstallError(
        "未找到 snap，且 VS Code 不在默认软件源中。请参考官方文档手动安装：\n"
        "        https://code.visualstudio.com/docs/setup/linux"
    )


def update_vscode(cfg: Config) -> None:
    if proc.which("snap"):
        cmd = " ".join(packages.sudo_prefix() + ["snap", "refresh", "code"])
        if proc.run_shell(cmd) != 0:
            warn("VS Code 更新可能未完全成功 (也可能已是最新版)，请检查 snap。")
        else:
            ok("VS Code 更新完成。")
        return
    warn("未检测到 snap 管理的 VS Code，请参考官方文档手动更新。")


def uninstall_vscode(cfg: Config) -> None:
    if proc.which("snap"):
        cmd = " ".join(packages.sudo_prefix() + ["snap", "remove", "code"])
        if proc.run_shell(cmd) != 0:
            raise InstallError("snap 卸载 VS Code 失败。")
        ok("VS Code 卸载完成。")
        return
    warn("未检测到 snap 管理的 VS Code，请参考官方文档手动卸载。")


def install_claude(cfg: Config) -> None:
    """Claude CLI：官方在线安装脚本 (bash)。"""
    proxy = cfg.proxy or ""
    prefix = f"export HTTP_PROXY='{proxy}' HTTPS_PROXY='{proxy}'; " if proxy else ""
    if proc.run_shell(prefix + "curl -fsSL https://claude.ai/install.sh | bash") != 0:
        raise InstallError("Claude 安装脚本执行失败。")
    proc.try_run(["claude", "--version"])


def update_claude(cfg: Config) -> None:
    """官方安装脚本本身具备更新能力，重新执行即可。"""
    install_claude(cfg)


def uninstall_claude(cfg: Config) -> None:
    claude_bin = Path.home() / ".local" / "bin" / "claude"
    if claude_bin.exists():
        claude_bin.unlink()
        ok("已删除 claude 可执行文件。")
    else:
        warn(f"未在 {claude_bin} 找到 claude 可执行文件，可能安装位置不同，需手动检查。")
    warn("用户目录下的 Claude 配置/缓存（如 ~/.claude）未被清理，需要的话请手动删除。")


def install_ccswith(cfg: Config) -> None:
    """ccswith：从 GitHub release 拉取最新版 Linux 资产，解压并通过 symlink 暴露到 ~/.local/bin。"""
    # TODO(setup): 替换为真实仓库 owner/repo 与资产命名规则。
    repo = "TODO/ccswith"
    proxy = cfg.proxy or ""
    proxy_prefix = f"export HTTP_PROXY='{proxy}' HTTPS_PROXY='{proxy}'; " if proxy else ""
    step(f"\n从 GitHub API 获取 {repo} 最新 release...")
    try:
        rel = net.github_latest(repo, proxy)
        version = rel["tag_name"]
        # TODO(setup): 按真实资产名调整（占位：ccswith-{version}-linux-x86_64.tar.gz）
        asset_name = f"ccswith-{version}-linux-x86_64.tar.gz"
        asset = next((x for x in rel["assets"] if x["name"] == asset_name), None)
        if asset is None:
            raise InstallError(f"未找到匹配的发行资产: {asset_name}")
        url = asset["browser_download_url"]
    except InstallError:
        raise
    except Exception as e:
        raise InstallError(f"获取 {repo} 最新 release 失败: {e}") from e

    install_path = Path.home() / ".local" / "ccswith" / version
    # TODO(setup): 按真实可执行文件名调整（占位：ccswith）
    exe = install_path / "ccswith"
    bin_link = Path.home() / ".local" / "bin" / "ccswith"
    if exe.exists():
        warn(f"ccswith {version} 已安装于: {install_path}，跳过。")
    else:
        install_path.parent.mkdir(parents=True, exist_ok=True)
        step(f"\n下载并解压 ccswith {version}...")
        archive_path = Path("/tmp") / asset_name
        cmd = proxy_prefix + (
            f"curl -fsSL -o {archive_path} {url} && "
            f"mkdir -p {install_path} && tar -xzf {archive_path} -C {install_path} --strip-components=1"
        )
        if proc.run_shell(cmd) != 0:
            raise InstallError("ccswith 下载/解压失败。")
        if not cfg.keep_archive:
            archive_path.unlink(missing_ok=True)
        ok("ccswith 部署成功!")
    bin_link.parent.mkdir(parents=True, exist_ok=True)
    if bin_link.exists() or bin_link.is_symlink():
        bin_link.unlink()
    bin_link.symlink_to(exe)
    proc.try_run(["ccswith", "--version"])


def update_ccswith(cfg: Config) -> None:
    uninstall_ccswith(cfg)
    install_ccswith(cfg)


def uninstall_ccswith(cfg: Config) -> None:
    base = Path.home() / ".local" / "ccswith"
    bin_link = Path.home() / ".local" / "bin" / "ccswith"
    if bin_link.exists() or bin_link.is_symlink():
        bin_link.unlink()
    if base.exists():
        shutil.rmtree(base, ignore_errors=True)
        ok("ccswith 卸载完成。")
    else:
        warn(f"未找到已安装的 ccswith（{base}），跳过。")


def install_omposh(cfg: Config) -> None:
    """Oh My Posh：官方安装脚本。"""
    proxy = cfg.proxy or ""
    prefix = f"export HTTP_PROXY='{proxy}' HTTPS_PROXY='{proxy}'; " if proxy else ""
    if proc.run_shell(prefix + "curl -s https://ohmyposh.dev/install.sh | bash -s") != 0:
        warn("Oh My Posh 安装可能未完全成功，请检查网络与依赖。")
    else:
        ok("Oh My Posh 安装完成。")


def update_omposh(cfg: Config) -> None:
    """官方安装脚本本身具备更新能力，重新执行即可。"""
    install_omposh(cfg)


def uninstall_omposh(cfg: Config) -> None:
    removed = False
    for candidate in (Path.home() / ".local" / "bin" / "oh-my-posh", Path.home() / "bin" / "oh-my-posh"):
        if candidate.exists():
            candidate.unlink()
            removed = True
    if removed:
        ok("Oh My Posh 卸载完成。")
    else:
        warn("未找到已安装的 oh-my-posh 可执行文件，可能安装位置不同，需手动检查。")


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
