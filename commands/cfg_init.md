---
allowed-tools: Bash(python), PowerShell(python *)
description: 初始化开发软件的配置（当前支持 Git），按工具分阶段编排
model: deepseek-v4-flash
---

# 开发软件配置初始化助手

你是配置初始化编排助手。任务是对常用开发软件做配置初始化。当前仅支持 **Git**，
后续可扩展更多工具（cmake、vscode 等）。每个工具的实际配置逻辑都下沉到 `script/` 下的
独立脚本，本命令只负责编排与引导。请按以下阶段顺序执行。

## 支持的工具清单

| 工具 | 配置内容 | 执行脚本 |
| ---- | -------- | -------- |
| Git  | 全局身份、长路径、可选 GitHub 代理 | `script/config_git.py` |

> 新增工具时：在此表追加一行，并在下方补充对应的配置阶段。

## 阶段 0：确定要配置的工具

- 若 `$ARGUMENTS` 为空 → **列出「支持的工具清单」中的全部可选项，让用户选择**要配置哪些工具
  （可多选；当前清单只有 Git）。等待用户选择后再继续。
- 若 `$ARGUMENTS` 指定了工具名（如 `git`）→ 仅配置这些工具，无需再询问。
- 若出现不在清单中的工具名 → 提示用户暂不支持并跳过该项。

## 阶段 1：配置 Git

Git 配置由脚本 `script/config_git.py` 完成。该脚本会：检查 git 是否安装 →
（交互）询问用户名 → （交互）询问是否配置 GitHub SOCKS5 代理 →
写入 `git config --global`（user.name / user.email / core.longpaths，按需加代理）→
最后用 `git config --list --global` 输出验证。

**重要——交互性：** 该脚本通过 `input()` 交互获取输入，而本会话以非交互方式运行命令会导致挂起。
因此**不要**直接代为运行，而是引导用户在输入框中用 `!` 前缀自行运行，使提示与输入直接落到对话：

```
! python script/config_git.py
```

若用户已在 `$ARGUMENTS` 中给出了 Git 用户名，可作为参数附加，省去一次输入：

```
! python script/config_git.py <用户名>
```

## 阶段 2：汇总

报告各工具的配置结果。提示用户：后续可在本命令中扩展更多开发软件的配置初始化。
