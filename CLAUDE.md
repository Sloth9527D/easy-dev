# CLAUDE.md

此文件为 Claude Code（claude.ai/code）在此仓库中工作时提供指导。

## 概述

`easy-dev` 是一个 Claude Code 插件，用于在 Windows 上自动化搭建 C/C++ 交叉编译开发环境。它通过 `SessionStart` 钩子在每次会话启动时运行环境检查，并提供一套 PowerShell 脚本安装完整工具链（Git、CMake、LLVM-MinGW、Python、VS Code、Oh My Posh、Claude CLI）。

## 架构

```
.claude-plugin/              # 插件标识与市场元数据
hooks/hooks.json             # SessionStart 钩子 → 运行 check_env.py
script/
  check_env.py               # 环境诊断脚本（Python）
  install_tools.py           # 跨平台安装 CLI 启动器
  install_tool/              # 安装包（按依赖倒置组织，平台实现隔离）
    cli.py                   # 高层 CLI，只依赖 core 抽象与 factory
    factory.py               # 平台选择接缝（运行时按平台惰性导入）
    core/                    # 平台无关抽象（config/console/net/archive/proc/base/gittemplate）
    windows/                 # Windows 实现（installers.py、env.py、scripts/*.ps1）
    linux/                   # Linux 实现（installers.py、packages.py）
```

插件清单（`.claude-plugin/plugin.json`）定义名称/版本/作者。钩子从 `hooks/hooks.json` 自动加载，无需在清单中显式引用。

依赖方向：`cli → factory → core 抽象 ← windows / linux 实现`。`core` 不导入任何平台模块；平台实现只在对应平台被 `factory` 导入，彼此隔离。

## 常用命令

- **运行环境检查：** `python script/check_env.py`
- **安装工具（跨平台）：** `python script/install_tools.py <工具...>` 或 `--all`；`--list` 查看全部，`python -m install_tool` 为等价入口
- **修改插件后重新加载：** `/reload-plugins`
- **诊断插件问题：** `/doctor`

无构建步骤、测试套件或代码检查配置。

## 关键说明

- `check_env.py` 检查以下工具：git、cmake、code（VS Code）、clang、python，输出 SessionStart 钩子格式的 JSON（`additionalContext` 为逗号分隔字符串，缺失工具标记为 `not_found`）。
- 安装 CLI 跨平台：Windows 下载官方压缩包/安装器并写用户级 PATH；Linux 调用系统包管理器（apt/dnf/yum/pacman/zypper）。
- 安装路径、下载目录、代理均可配置（`--dev-root` / `--download-dir` / `--proxy`），默认值随平台变化（Windows 默认 `E:\Dev`、`E:\Downloads`）。
- 安装具有幂等性（Windows 检查目标目录是否已存在；Linux 依赖包管理器自身）。
- `install_tool/windows/scripts/` 下保留了原始 `.ps1` 脚本（含命名有误的 `install_vscode.ps1`，实际安装 VS Code System Installer），现已由 Python CLI 取代，仅作 Python 缺失时的引导兜底。
