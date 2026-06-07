"""跨平台共享：生成并配置全局 git commit 模板。"""
from __future__ import annotations

import subprocess
from pathlib import Path

from .console import err, ok, step, warn
from .proc import which

_TEMPLATE = """# <type>(<scope>): <subject>
# |<----  尽量限制在 50 个字符以内  ---->|
#
# <body>
# 详细描述本次修改的动机、背景以及具体的变更。
# |<----   每行尽量限制在 72 个字符以内，解释 WHY 和 WHAT，而不是 HOW   ---->|
#
# <footer>
# 用于记录 Breaking Changes (破坏性变更) 或关闭的 Issue (例如: Fixes #123)
#
# ----------------------------------------------------------------------
# <type> 类型说明:
#   feat     : 新增功能 (Feature)
#   fix      : 修复 Bug
#   docs     : 文档更新 (Documentation)
#   style    : 代码格式修改 (不影响代码运行的变动，如空格、格式化等)
#   refactor : 代码重构 (既不是新增功能，也不是修复 Bug 的代码变动)
#   perf     : 性能优化 (Performance)
#   test     : 增加或修改测试用例
#   build    : 构建系统或外部依赖项的更改 (如 CMake, LLVM, Cargo 等)
#   ci       : CI 配置文件和脚本的更改 (如 GitHub Actions)
#   chore    : 杂项，其他不修改源代码或测试文件的更改
# ----------------------------------------------------------------------
"""


def configure_git_template() -> None:
    """生成 ~/.gitmessage 并配置为全局 commit.template。"""
    step("\n配置全局 Git commit 模板...")
    template_path = Path.home() / ".gitmessage"
    template_path.write_text(_TEMPLATE, encoding="utf-8")
    ok(f"已生成模板文件: {template_path}")

    git = which("git")
    if not git:
        warn("未找到 git 命令，跳过 commit.template 配置。")
        return
    try:
        subprocess.run([git, "config", "--global", "commit.template", str(template_path)])
        ok("已配置全局 git commit.template。")
    except Exception as e:
        err(f"配置 git commit.template 失败: {e}")
