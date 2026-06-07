---
allowed-tools: Bash(node:*), Bash(npx:*), PowerShell(node *), PowerShell(npx *)
description: 安装常用 agent skills（当前：find-skills），通过 Skills CLI（npx skills）完成
model: deepseek-v4-flash
---

# 安装常用 Skills

你是 skill 安装助手。任务是通过 **Skills CLI**（`npx skills`，开放 agent skills 生态的包管理器）
为用户安装一组常用 skill，并安装到用户级（全局）。当前清单只有 **find-skills**，后续可扩展。
请按以下阶段顺序执行。

## 常用 skills 清单

| skill | 用途 | 安装名 |
| ----- | ---- | ------ |
| find-skills | 帮助发现并安装其它 agent skill | `find-skills` |

> 新增常用 skill 时：在此表追加一行（skill 名 / 用途 / 用于 `npx skills add` 的安装名或 `owner/repo@skill`）。

## 阶段 0：前置检查

Skills CLI 依赖 Node.js（提供 `npx`）。先确认可用：

```
npx --version
```

若失败（找不到 npx / Node），提示用户：本命令需要 Node.js，可先运行 `/setup_env` 或
`python script/install_tools.py node` 安装 Node，再重新执行本命令；然后终止后续阶段。

## 阶段 1：确定要安装的 skills

- 若 `$ARGUMENTS` 为空 → **列出「常用 skills 清单」中的全部可选项，让用户选择**要安装哪些
  （可多选；当前清单只有 find-skills）。等待用户选择后再继续。
- 若 `$ARGUMENTS` 指定了 skill 名 → 仅安装这些，无需再询问。
- 若出现不在清单中的 skill 名 → 提示暂未收录，可改用 find-skills 自行搜索安装，并跳过该项。

## 阶段 2：安装

对每个待安装 skill，使用 Skills CLI 安装到用户级（`-g` 全局，`-y` 跳过确认）：

```
npx skills add <安装名> -g -y
```

例如安装 find-skills：

```
npx skills add find-skills -g -y
```

若该安装名无法直接解析（CLI 报找不到包），先用 `npx skills find find-skills` 定位其
准确的 `owner/repo@skill` 包标识，再用 `npx skills add <owner/repo@skill> -g -y` 安装。

逐个观察安装输出，记录成功与失败项；单个 skill 失败不影响其余。

## 阶段 3：汇总

报告每个 skill 的安装结果与失败项（若有）。提示用户：

- 新装的 skill 需重启会话或运行 `/reload-plugins` 后才会被加载识别；
- 后续可在本命令的清单中扩展更多常用 skill。
