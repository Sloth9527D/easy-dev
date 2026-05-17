# CLAUDE.md

此文件为 Claude Code（claude.ai/code）在此仓库中工作时提供指导。

## 概述

`easy-dev` 是一个 Claude Code 插件，用于在 Windows 上自动化搭建 C/C++ 交叉编译开发环境。它通过 `SessionStart` 钩子在每次会话启动时运行环境检查，并提供一套 PowerShell 脚本安装完整工具链（Git、CMake、LLVM-MinGW、Python、VS Code、Oh My Posh、Claude CLI）。

## 架构

```
.claude-plugin/          # 插件标识与市场元数据
hooks/hooks.json         # SessionStart 钩子 → 运行 check_env.py
script/
  check_env.py           # 环境诊断脚本（Python，支持 --json）
  install_tool/window/   # 各工具的 PowerShell 安装脚本
```

插件清单（`.claude-plugin/plugin.json`）定义名称/版本/作者。钩子从 `hooks/hooks.json` 自动加载，无需在清单中显式引用。

## 常用命令

- **运行环境检查：** `python script/check_env.py`（人类可读输出）或 `python script/check_env.py --json`（结构化输出）
- **安装工具：** 在 PowerShell 中运行对应的 `script/install_tool/window/install_<名称>.ps1` 脚本
- **修改插件后重新加载：** `/reload-plugins`
- **诊断插件问题：** `/doctor`

无构建步骤、测试套件或代码检查配置。

## 关键说明

- `check_env.py` 检查以下工具：git、cmake、code（VS Code）、clang、clang++、python。在非 Windows 系统上打印跳过信息后退出。
- 所有安装脚本使用硬编码路径 `E:\Dev\`，并假定 HTTP 代理位于 `127.0.0.1:10808`。这些是作者机器的特定配置。
- `install_vscode.ps1` 命名有误——实际安装的是 PortableGit，而非 VS Code。
- 安装脚本具有幂等性（如果目标路径已存在对应工具则跳过）。
