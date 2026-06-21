# 阶段 2：创建隔离工作区（Git Worktree）

为已批准的 spec 开一个独立的 git worktree + 新分支，让本次开发与主工作区的改动互不干扰，并在开工前确认测试基线没有提前损坏。

## 为什么这样设计

在主工作区里直接切分支开发，容易和用户手头未提交的改动打架，也不方便并行处理多个 spec。Worktree 在磁盘上开一个新目录、共享同一个 `.git`，互相隔离又不必克隆整个仓库。开工前先确认测试基线干净，避免后续把"别人挖的坑"误判成自己改坏的。

## 适用判断

紧接在阶段 1 产出的 spec 被用户批准之后；本阶段默认**直接创建**，不必为创建动作本身二次确认（用户已通过批准 spec 表达了开工意愿）——但创建失败（如分支已存在、worktree 路径冲突）时要停下来如实汇报，不强行覆盖。

## 执行步骤

### 1. 确定分支名与 worktree 路径

从 spec 的 `<slug>` 命名分支：`feature/<slug>`。worktree 放在仓库同级目录，避免嵌套进当前仓库：

```powershell
$repoRoot = git rev-parse --show-toplevel
$repoName = Split-Path $repoRoot -Leaf
$slug = "<slug>"
$worktreePath = Join-Path (Split-Path $repoRoot -Parent) "$repoName.worktrees\$slug"
```

若该路径已存在，先用 `git worktree list` 确认是否是同一功能遗留的工作区——如果是，直接复用并告知用户；如果是无关内容，停下来询问用户如何处理，不要静默覆盖。

### 2. 创建分支与 worktree

```powershell
git worktree add -b "feature/$slug" $worktreePath
```

如果 `feature/<slug>` 分支已存在（例如上次中断过），改用：

```powershell
git worktree add $worktreePath "feature/$slug"
```

### 3. 验证测试基线

进入新 worktree，运行本仓库的测试命令（若 `CLAUDE.md` 或上下文文档未记录测试命令，说明这个仓库当前没有配置测试套件——如实告知用户"无测试基线可验证"，不要编造测试命令）。

```powershell
PowerShell -Command "cd $worktreePath; <测试命令若存在>"
```

若基线已经是红的（在你接触之前就失败），明确告知用户当前基线状态，不要把它当成自己引入的问题，也不要尝试擅自修复——除非这正是本次 spec 要解决的问题。

### 4. 汇报并交接

告知用户：分支名、worktree 路径、测试基线结果。下一步是阶段 3（微级计划），把 spec 拆成原子任务计划。
