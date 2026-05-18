---
allowed-tools: Bash(git:*), Bash(git config:*)
description: 初始化 Git 全局配置（用户身份、长路径、可选代理）
model: deepseek-v4-flash
---

# 初始化 Git 全局配置

为当前用户设置 Git 全局身份与常用选项，可选配置 GitHub SOCKS5 代理。

## 执行流程

### 1. 前置检查

确认 git 已安装：

```bash
git --version
```

如命令不存在，提示用户先安装 Git，终止流程。

### 2. 获取用户名

- 若 `$ARGUMENTS` 非空，直接使用其值作为 `user.name`
- 若为空，询问用户：**请输入你的 Git 用户名：**

### 3. 询问是否配置代理

询问用户：

> 是否为 GitHub 配置本地 SOCKS5 代理（127.0.0.1:10808）？[y/N]

- 回答 `y` → 执行步骤 4 的完整版
- 其他 → 跳过代理配置

### 4. 执行配置

```bash
git config --global user.name "$USER_NAME"
git config --global user.email "p479764650@gmail.com"
git config --global core.longpaths true
```

如需代理，额外执行：

```bash
git config --global http.https://github.com.proxy socks5://127.0.0.1:10808
```

### 5. 验证结果

```bash
git config --list --global
```

输出配置列表，确认各项已生效。

## 注意事项

- 此操作会**覆盖**已有的同名全局配置，执行前请确认
- 代理地址 `127.0.0.1:10808` 为本地地址，需确保代理服务正在运行
- 如需修改单项配置，直接运行对应的 `git config --global <key> <value>`
- `core.longpaths` 仅在 Windows 上有实际效果，Linux/macOS 可忽略
