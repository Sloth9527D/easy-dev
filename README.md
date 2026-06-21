# easy-dev

一个 Claude Code 插件，提供跨平台（Windows / Linux）开发工具链安装、会话启动时的环境自动诊断，以及一组把安装、Git 配置、提交、文件转换、研发工作流等常见操作包装成可调用助手的 slash 命令与技能。

## 前置要求

| 依赖 | 说明 |
|------|------|
| **Claude Code** | 需支持插件机制的版本（`/plugin` 命令可用） |
| **Python 3** | **必需**。插件的 `SessionStart` 钩子会运行 `python check_env.py` 做环境诊断；安装 CLI（`script/install_tools.py`）也基于 Python。请确保 `python` 在 PATH 上 |
| **Git** | 安装方式一（从 GitHub 拉取）需要 |

> 若机器上还没有 Python，可先手动安装（Windows 从 https://www.python.org 下载，Linux 用系统包管理器 `apt/dnf/...` 安装 `python3`），装好后再安装本插件。

## 安装

### 方式一：从 GitHub 市场安装（推荐）

在 Claude Code 会话中依次执行：

```
/plugin marketplace add Sloth9527D/easy_dev
/plugin install easy-dev@easy-dev
```

- 第一条把本仓库注册为一个插件市场（`Sloth9527D/easy_dev` 是 GitHub 仓库路径，市场名为 marketplace.json 定义的 `easy-dev`）。
- 第二条安装其中的 `easy-dev` 插件。`@` 后面是市场名，格式为 `<插件名>@<市场名>`。

也可以只执行 `/plugin`，在交互界面里选择市场与插件完成安装。

### 方式二：本地安装（开发 / 离线）

已经把仓库克隆到本地时，直接把本地目录作为市场添加：

```
/plugin marketplace add C:\Users\p4797\.claude\plugins\easy_dev
/plugin install easy-dev@easy-dev
```

把路径换成你本地仓库的实际位置即可（Linux 用对应的 POSIX 路径）。本地市场便于改动后立即生效，配合 `/reload-plugins` 调试。

## 验证安装

1. 重启一个 Claude Code 会话——`SessionStart` 钩子会自动运行环境诊断，可在会话上下文里看到 `git / cmake / python / vscode / llvm` 等工具的版本或 `not_found` 标记。
2. 输入 `/` 查看命令列表，应能看到 `cfg_init`、`commit`、`setup_env`、`setup_skills`。
3. 技能（如 `dev-flow`、`code-inspect`、`file2md` 等）会在匹配到相关请求时自动触发，无需手动调用。

如改动了插件文件，用 `/reload-plugins` 重新加载；排查问题用 `/doctor`。

## 包含的能力

- **Slash 命令**（`commands/`）：`cfg_init`（初始化 Git 等配置）、`commit`（Conventional Commits 提交）、`setup_env`（诊断并安装缺失工具链）、`setup_skills`（安装常用 agent skills）。
- **技能**（`skills/`）：`dev-flow`（7 阶段研发工作流）、`code-inspect`（独立代码检视）、`file2md`（任意文件转 Markdown）、`ctx-gen`（生成项目上下文文档）、`bak-claude-cfg`（备份 Claude 配置到 GitHub）、`karpathy-guidelines`（编码行为准则）。
- **钩子**（`hooks/`）：`SessionStart` 时运行 `script/check_env.py` 诊断环境。
- **安装 CLI**（`script/`）：`python script/install_tools.py <工具...>` 或 `--all` 跨平台安装 Git / CMake / LLVM-MinGW / Python / Node.js / VS Code / Oh My Posh / Claude CLI 等；`--list` 查看全部。

## 卸载

```
/plugin uninstall easy-dev@easy-dev
```

如不再需要该市场，可一并移除：

```
/plugin marketplace remove easy-dev
```

## 已知注意事项

- 插件主要面向 Windows（PowerShell），安装 CLI 同时支持 Linux（调用系统包管理器）。
- 市场注册命令中的 `Sloth9527D/easy_dev` 是 GitHub 仓库名（带下划线），与插件名 / 市场名 `easy-dev`（连字符）不是一回事，不要混淆。
