# CLAUDE.md

此文件为 Claude Code（claude.ai/code）在此仓库中工作时提供指导。

## 概述

`easy-dev` 是一个 Claude Code 插件，包含三部分能力：(1) 跨平台（Windows / Linux）的开发工具链安装 CLI；(2) `SessionStart` 钩子在每次会话启动时自动诊断环境；(3) 一组 slash 命令（`commands/`）与技能（`skills/`），把安装、Git 配置、提交、文件转换等常见操作包装成可调用的助手。工具链覆盖 Git、CMake、LLVM-MinGW、Python、Node.js、VS Code、Oh My Posh、Claude CLI、ccswith。

## 架构

```
.claude-plugin/              # 插件标识与市场元数据（plugin.json / marketplace.json）
hooks/hooks.json             # SessionStart 钩子 → check_env.py；Stop 钩子 → notify_done.py
commands/                    # slash 命令（cfg_init / commit / setup_env / setup_skills / fix_build），多为编排安装 CLI 的提示词
skills/                      # 技能（bak-claude-cfg / file2md / karpathy-guidelines / ctx-gen / code-inspect / dev-flow / dt），含 SKILL.md、可选 evals/、可选 stages/ 等附属文件
script/
  check_env.py               # 环境诊断脚本（Python）
  notify_done.py             # Stop 钩子：任务完成时弹系统通知 + 提示音（Python，跨平台）
  install_tools.py           # 跨平台安装 CLI 启动器
  install_tool/              # 安装包（按依赖倒置组织，平台实现隔离）
    cli.py                   # 高层 CLI，只依赖 core 抽象与 factory
    factory.py               # 平台选择接缝（运行时按平台惰性导入）
    core/                    # 平台无关抽象（config/console/net/archive/proc/base/gittemplate）
    windows/                 # Windows 实现（installers.py、env.py、scripts/*.ps1）
    linux/                   # Linux 实现（installers.py、packages.py）
```

插件清单（`.claude-plugin/plugin.json`）定义名称/版本/作者。钩子从 `hooks/hooks.json` 自动加载，命令与技能从对应目录自动发现，均无需在清单中显式引用。`hooks.json` 当前注册两个事件：`SessionStart`（跑 `check_env.py` 诊断环境）与 `Stop`（跑 `notify_done.py`，Claude 完成一轮回复时弹系统通知 + 提示音）。`notify_done.py` 按平台用无第三方依赖的方式提醒（Windows: winsound + NotifyIcon 气泡；macOS: osascript；Linux: notify-send + 可用的声音播放器），通知放进分离子进程、所有异常静默吞掉并始终退出 0，确保绝不阻塞或中断会话。

依赖方向：`cli → factory → core 抽象 ← windows / linux 实现`。`core` 不导入任何平台模块；平台实现只在对应平台被 `factory` 导入，彼此隔离。新增可装工具 = 在 `windows/installers.py` 与 `linux/installers.py` 各自的 `REGISTRY`（`PlatformRegistry`）中注册一个安装函数；CLI 与 `core` 无需改动。

## 命令与技能层

`commands/*.md` 与 `skills/*/SKILL.md` 都是带 YAML frontmatter 的提示词文件（非可执行代码），由 Claude Code 在运行时加载。多数命令是对底层脚本的“编排说明”而非独立逻辑——例如 `setup_env` 命令完整描述了「检查 Python → 跑 check_env.py → 解析缺失工具 → 调 install_tools.py」的分阶段流程。修改这类行为时，往往要同时改 frontmatter 描述、提示词步骤，以及它所调用的脚本。

frontmatter 两个约定值得注意：(1) `allowed-tools` 收窄该命令可用的工具，且常同时声明 Bash 与 PowerShell 两种形式以跨平台（如 `Bash(python), PowerShell(python *)`）；(2) 纯编排类命令（`cfg_init` / `setup_env` / `setup_skills`）固定 `model: deepseek-v4-flash` 走更省的模型，而需要更强推理的 `commit` 不固定模型。

## 7 阶段研发工作流（dev-flow 技能）

`skills/dev-flow/` 是一个**单一技能**，覆盖完整的 5 大阶段（含两道卡点）研发工作流。采用渐进式披露结构：`SKILL.md` 是编排入口（阶段总览 + 阶段判定逻辑），各阶段的详细执行步骤拆在 `skills/dev-flow/stages/*.md`，由 SKILL.md 按需引导 Read。该技能靠 description 自动触发，无对应 slash 命令。

| 阶段 | 步骤文件（stages/） |
|------|-------|
| 需求澄清 | `brainstorming.md` |
| 隔离工作区 | `using-git-worktrees.md` |
| 微级计划 | `writing-plans.md` |
| 派发执行（内含两道卡点） | `subagent-driven-development.md` → `test-driven-development.md` + `requesting-code-review.md` |
| 收尾清理 | `finishing-a-development-branch.md` |

各阶段产出统一落在 `.claude/dev-flow/<slug>/`（`spec.md`、`plan.md`）。这是一套对非 trivial 开发任务具有强制约束力的规范（参见各 stages 文件的"为什么这样设计/适用判断"），而非可选建议。改 SKILL.md 的阶段判定逻辑或某阶段步骤时，往往要同步改对应的 `stages/*.md`。worktree 创建阶段按约定直接执行，无需二次确认；TDD 约束目前仅靠文字自查，没有自动化 hook 拦截。注意工作流内的任务间审查（`stages/requesting-code-review.md`）对照 spec/plan，与独立的 `code-inspect` 技能（通用代码检视）定位不同。

## 常用命令

- **运行环境检查：** `python script/check_env.py`
- **安装工具（跨平台）：** `python script/install_tools.py <工具...>` 或 `--all`；`--list` 查看全部，`python -m install_tool` 为等价入口
- **初始化 Git 全局配置：** `python script/config_git.py [用户名]`（交互询问用户名与可选代理；对应 `/cfg_init` 命令）
- **修改插件后重新加载：** `/reload-plugins`
- **诊断插件问题：** `/doctor`

无构建步骤、单元测试框架或 lint 配置——脚本靠手动运行验证。技能行为的回归用 evals 样例覆盖（目前只有 `skills/file2md/evals/evals.json`），通过 `skill-creator` 技能运行；新增/修改技能时若有对应 evals，应一并更新。面向最终用户的安装/卸载步骤见 `README.md`，本文件聚焦于在仓库内开发插件本身。

## 关键说明

- `check_env.py` 检查以下工具：git、cmake、code（VS Code）、clang、python，输出 SessionStart 钩子格式的 JSON（`additionalContext` 为逗号分隔字符串，缺失工具标记为 `not_found`）。
- 安装 CLI 跨平台：Windows 下载官方压缩包/安装器并写用户级 PATH；Linux 调用系统包管理器（apt/dnf/yum/pacman/zypper）。
- 安装路径、下载目录、代理均可配置（`--dev-root` / `--download-dir` / `--proxy`），默认值随平台变化（Windows 默认 `E:\Dev`、`E:\Downloads`）。
- 安装具有幂等性（Windows 检查目标目录是否已存在；Linux 依赖包管理器自身）。单个工具失败不中断其余工具，结尾汇总失败列表。
- 可装工具多于环境诊断范围：`check_env.py` 只看 git/cmake/code/clang/python，而安装 CLI 还支持 node / claude / omposh / ccswith 等（`--list` 查看全部）。`PlatformRegistry.all_order` 决定 `--all` 安装哪些工具，会刻意排除依赖外部源的可选项。
- `install_tool/windows/scripts/` 下保留了原始 `.ps1` 脚本（含命名有误的 `install_vscode.ps1`，实际安装 VS Code System Installer），现已由 Python CLI 取代，仅作 Python 缺失时的引导兜底。
