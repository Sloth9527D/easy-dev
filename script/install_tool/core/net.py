"""网络相关：带进度的下载、GitHub release 元数据获取、各官方源最新版本探测。"""
from __future__ import annotations

import json
import re
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


def _fetch_json(url: str, proxy: str | None = None) -> dict:
    opener = _build_opener(proxy)
    with opener.open(url, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def github_latest(repo: str, proxy: str | None = None) -> dict:
    """获取 GitHub 仓库最新 release 元数据 (repo 形如 'mstorsjo/llvm-mingw')。"""
    return _fetch_json(f"https://api.github.com/repos/{repo}/releases/latest", proxy)


def latest_node_version(proxy: str | None = None) -> str:
    """从 nodejs.org 官方版本索引获取最新 Node.js 版本号 (不含前导 v)。"""
    data = _fetch_json("https://nodejs.org/dist/index.json", proxy)
    if not data:
        raise InstallError("nodejs.org 版本索引为空。")
    return data[0]["version"].lstrip("v")


def latest_python_version(proxy: str | None = None) -> str:
    """从 python.org 官方 API 获取最新稳定 (非预发布) 版 Python 版本号。"""
    url = (
        "https://www.python.org/api/v2/downloads/release/"
        "?is_published=true&pre_release=false&ordering=-release_date&page_size=10"
    )
    data = _fetch_json(url, proxy)
    for item in data.get("results", []):
        m = re.fullmatch(r"Python (\d+\.\d+\.\d+)", item.get("name", ""))
        if m:
            return m.group(1)
    raise InstallError("未能从 python.org 解析出最新稳定版本号。")
