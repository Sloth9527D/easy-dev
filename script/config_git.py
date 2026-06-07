#!/usr/bin/env python3
"""初始化 Git 全局配置：用户身份、长路径、可选 GitHub SOCKS5 代理。

可直接运行：交互询问用户名与是否配置代理。
也可把用户名作为第一个参数传入以免去输入：python config_git.py <用户名>
"""
import shutil
import subprocess
import sys

# 默认邮箱与代理地址，按需直接修改这两个常量。
USER_EMAIL = "p479764650@gmail.com"
PROXY_ADDR = "socks5://127.0.0.1:10808"


def run(args):
    """回显并执行命令，失败抛出 CalledProcessError。"""
    print("+", " ".join(args))
    subprocess.run(args, check=True)


def main():
    # 1. 前置检查：git 是否安装
    if shutil.which("git") is None:
        print("未找到 git，请先安装 Git 后重试。")
        return 1

    # 2. 获取用户名（优先用命令行参数，否则循环询问直到非空）
    name = sys.argv[1].strip() if len(sys.argv) > 1 else ""
    while not name:
        name = input("请输入你的 Git 用户名：").strip()

    # 3. 询问是否配置代理
    ans = input(
        "是否为 GitHub 配置本地 SOCKS5 代理（127.0.0.1:10808）？[y/N] "
    ).strip().lower()
    use_proxy = ans in ("y", "yes")

    # 4. 执行配置
    run(["git", "config", "--global", "user.name", name])
    run(["git", "config", "--global", "user.email", USER_EMAIL])
    run(["git", "config", "--global", "core.longpaths", "true"])
    if use_proxy:
        run([
            "git", "config", "--global",
            "http.https://github.com.proxy", PROXY_ADDR,
        ])

    # 5. 验证结果
    print("\n当前 Git 全局配置：")
    subprocess.run(["git", "config", "--list", "--global"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
