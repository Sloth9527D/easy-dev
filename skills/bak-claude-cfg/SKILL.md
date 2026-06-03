---
name: bak-claude-cfg
description: 将 Claude Code 的 settings.json 备份到 GitHub 仓库，并按操作系统分目录存放。当用户提到备份配置、同步 settings、把 Claude 设置推到 GitHub、在多台机器间同步配置，或想保存/恢复 Claude Code 设置时，请使用此技能——即使用户没有明确说"备份"二字。
allowed-tools:
  - PowerShell(git*) # 在 PowerShell 中执行 git 与文件操作
  - Read # 读取并校验 settings.json
---

# 备份 Claude 配置到 GitHub

把本机的 `settings.json` 推送到一个集中的 GitHub 仓库，按操作系统分目录（`windows/`、`macos/`、`linux/`）存放。这样不同机器的配置互不覆盖，又能随时取回查看或恢复。

## 为什么这样设计

不同操作系统的 `settings.json` 往往不同——路径用反斜杠还是正斜杠、装了哪些插件、代理设置等都不一样。如果所有机器共用一个文件，就会互相覆盖。按 OS 分目录能让每台机器有自己的"槽位"，而仓库历史天然成了配置的版本快照。

## 默认配置

下面是默认值，执行前可按用户的实际情况调整：

- **远程仓库**：`git@github.com:Sloth9527D/claude_settings.git`
- **本地工作副本**：Windows 用 `E:\Dev\claude_settings`，macOS/Linux 用 `~/claude_settings`
- **源文件**：Windows `$env:USERPROFILE\.claude\settings.json`，macOS/Linux `~/.claude/settings.json`

如果用户给了不同的仓库地址或本地路径，以用户的为准。

## 操作步骤

整个流程是「准备本地仓库 → 复制文件 → 提交推送」。本插件主要面向 Windows，下面以 PowerShell 为主，并在每步给出 macOS/Linux 的等价做法。

### 1. 确定操作系统与路径

先判断当前系统，映射到对应子目录：

| 操作系统 | 子目录 | 源 settings.json |
|---|---|---|
| Windows | `windows/` | `$env:USERPROFILE\.claude\settings.json` |
| macOS | `macos/` | `~/.claude/settings.json` |
| Linux | `linux/` | `~/.claude/settings.json` |

在 Claude Code 里可以直接从环境信息得知当前平台（`win32` / `darwin` / `linux`），无需额外探测命令。

### 2. 准备本地工作副本（不存在则 clone，存在则 pull）

这一步保证本地副本是最新的，避免推送时与远程冲突。

**Windows (PowerShell)：**
```powershell
$repo = "git@github.com:Sloth9527D/claude_settings.git"
$local = "E:\Dev\claude_settings"
if (Test-Path "$local\.git") {
    git -C $local pull --ff-only
} else {
    git clone $repo $local
}
```

**macOS/Linux (bash)：**
```bash
repo="git@github.com:Sloth9527D/claude_settings.git"
local="$HOME/claude_settings"
if [ -d "$local/.git" ]; then
    git -C "$local" pull --ff-only
else
    git clone "$repo" "$local"
fi
```

如果 `pull --ff-only` 失败（说明本地有未推送的提交或冲突），先停下来把情况告诉用户，让他决定如何处理，不要强行覆盖——配置文件丢了不好恢复。

### 3. 复制 settings.json 到对应子目录

确保子目录存在，然后复制。

**Windows (PowerShell)：**
```powershell
$dst = "$local\windows"
New-Item -ItemType Directory -Force -Path $dst | Out-Null
Copy-Item "$env:USERPROFILE\.claude\settings.json" "$dst\settings.json" -Force
```

**macOS/Linux (bash)：** 把 `windows` 换成 `macos` 或 `linux`：
```bash
dst="$local/macos"   # 或 linux
mkdir -p "$dst"
cp "$HOME/.claude/settings.json" "$dst/settings.json"
```

复制前用 Read 工具确认源文件是合法 JSON（能正常读取、不为空），避免把损坏的配置备份上去。

### 4. 提交并推送

只有在确实有变更时才提交——`settings.json` 没动的话不必产生空提交。

**Windows (PowerShell)：**
```powershell
git -C $local add windows/settings.json
if (git -C $local status --porcelain) {
    git -C $local commit -m "chore(windows): 备份 settings.json"
    git -C $local push
} else {
    Write-Output "settings.json 无变更，跳过提交"
}
```

**macOS/Linux (bash)：** 把 `windows` 换成对应目录，提交信息里的 scope 也相应调整（`macos` / `linux`）：
```bash
git -C "$local" add macos/settings.json
if [ -n "$(git -C "$local" status --porcelain)" ]; then
    git -C "$local" commit -m "chore(macos): 备份 settings.json"
    git -C "$local" push
else
    echo "settings.json 无变更，跳过提交"
fi
```

### 5. 汇报结果

告诉用户：备份到了哪个子目录、本次提交的 commit 信息（或"无变更已跳过"）、以及远程仓库地址。如果某一步失败了，如实说明卡在哪、报错是什么。

## 恢复配置（反向操作）

如果用户想从仓库恢复某台机器的配置，方向反过来：`git pull` 后把对应子目录的 `settings.json` 复制回 `~/.claude/`。覆盖本机配置前，先提示用户当前文件会被替换，确认后再操作。
