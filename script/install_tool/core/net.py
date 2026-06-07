"""网络相关：带进度的下载、GitHub release 元数据获取。"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

from .config import InstallError
from .console import ok


def _build_opener(proxy: str | None) -> urllib.request.OpenerDirector:
    handlers: list = []
    if proxy:
        handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    opener = urllib.request.build_opener(*handlers)
    opener.addheaders = [("User-Agent", "easy-dev-installer/1.0")]
    return opener


def download(url: str, dest: Path, proxy: str | None = None) -> Path:
    """下载 url 到 dest；若文件已存在则跳过。带简单进度显示。"""
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0:
        ok(f"已存在下载文件，跳过下载: {dest}")
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    opener = _build_opener(proxy)

    try:
        with opener.open(url, timeout=60) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            done = 0
            chunk = 1024 * 256
            with open(tmp, "wb") as f:
                while True:
                    buf = resp.read(chunk)
                    if not buf:
                        break
                    f.write(buf)
                    done += len(buf)
                    if total:
                        pct = done * 100 // total
                        mb = done / 1024 / 1024
                        sys.stdout.write(f"\r   下载中 {pct:3d}%  ({mb:6.1f} MB)")
                        sys.stdout.flush()
        if total:
            sys.stdout.write("\n")
        tmp.replace(dest)
    except Exception as e:
        if tmp.exists():
            tmp.unlink()
        raise InstallError(f"下载失败: {url}\n        {e}") from e

    ok(f"下载完成: {dest}")
    return dest


def github_latest(repo: str, proxy: str | None = None) -> dict:
    """获取 GitHub 仓库最新 release 元数据 (repo 形如 'mstorsjo/llvm-mingw')。"""
    api = f"https://api.github.com/repos/{repo}/releases/latest"
    opener = _build_opener(proxy)
    with opener.open(api, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))
