"""压缩包解压 (纯 Python zipfile，替代原脚本中的 tar)。"""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


def extract_zip_flatten(zip_path: Path, install_path: Path) -> None:
    """解压 zip，将其内部唯一顶层目录中的内容铺平到 install_path。

    适用于压缩包形如 `pkg-x.y/...` 的情况 (CMake、llvm-mingw、Node.js)。
    """
    install_path = Path(install_path)
    tmp = Path(zip_path).parent / (Path(zip_path).stem + "_extract_tmp")
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)

    try:
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmp)

        subdirs = [p for p in tmp.iterdir() if p.is_dir()]
        has_top_file = any(p.is_file() for p in tmp.iterdir())
        # 若恰好只有一个顶层目录且无顶层文件，则铺平；否则整体复制
        src = subdirs[0] if len(subdirs) == 1 and not has_top_file else tmp

        install_path.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            target = install_path / item.name
            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
            else:
                shutil.copy2(item, target)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def extract_zip_direct(zip_path: Path, install_path: Path) -> None:
    """将 zip 内容直接解压到 install_path (内容已在压缩包根目录，如 MinGit)。"""
    install_path = Path(install_path)
    install_path.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(install_path)
