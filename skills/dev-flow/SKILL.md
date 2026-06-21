---
name: dev-flow
description: 完整的 7 阶段研发工作流（需求澄清→隔离工作区→微级计划→自动化派发执行（含 TDD 与代码评审两道卡点）→收尾清理）。当用户提出一个非 trivial 的新功能需求，或想续接一条已有的功能开发流程时使用此技能：先判断当前所处阶段，再读取对应阶段的详细步骤执行。纯 bug 修复、已有精确规格的小改动、文档类改动不必触发。各阶段的详细指令在本技能目录的 stages/ 下。
allowed-tools:
  - Skill
  - Read
  - Glob
  - Grep
  - PowerShell(git*)
  - Edit
  - Write
  - AskUserQuestion
  - TaskCreate
  - TaskList
  - TaskGet
  - TaskUpdate
  - Agent
---

# 研发工作流

这是一套对开发任务具有强制约束力的 7 阶段研发工作流。**你是这套流程的执行者**：先判断当前处于哪个阶段，再读取该阶段对应的 `stages/<阶段>.md` 文件按其步骤执行，并在阶段之间维持状态。这是规范而非可选建议——除非用户明确要求跳过某个阶段。

每个阶段的详细执行步骤都单独放在本技能目录的 `stages/` 下，**不要凭记忆执行，进入某阶段时先 Read 对应文件**。

## 阶段总览

| 阶段 | 详细步骤文件 | 产出 | 进入下一阶段的条件 |
|------|------------|------|----------------------|
| 1. 需求澄清 | `stages/brainstorming.md` | `.claude/dev-flow/<slug>/spec.md` | 用户明确批准 spec |
| 2. 隔离工作区 | `stages/using-git-worktrees.md` | 新分支 + worktree，测试基线结论 | worktree 创建成功（自动，无需二次确认） |
| 3. 微级计划 | `stages/writing-plans.md` | `.claude/dev-flow/<slug>/plan.md` + 已登记的原子任务 | 用户下达"开始执行" |
| 4. 派发执行 | `stages/subagent-driven-development.md`（内部串联 `stages/test-driven-development.md` 与 `stages/requesting-code-review.md` 两道卡点） | 全部原子任务 `completed` | 任务清单全部完成，且无未解决的 Critical 问题 |
| 5. 收尾清理 | `stages/finishing-a-development-branch.md` | 分支处理结果 + worktree 清理 | 用户选定收尾方式并执行完毕 |

## 阶段判定逻辑

用户给出的可能是一段功能描述（开启新流程）或一个已存在的 `<slug>`（续接已有流程）。按以下顺序判断当前所处阶段，然后 Read 对应的步骤文件执行：

1. **没有可识别的 `<slug>`，且 `.claude/dev-flow/` 下找不到匹配的目录** → 新需求，进入阶段 1（`stages/brainstorming.md`）。
2. **存在 `.claude/dev-flow/<slug>/spec.md` 但用户尚未表达批准** → 留在阶段 1，把 spec 展示给用户等待批准；不要自行判定"看起来没问题"就视为批准。
3. **spec 已批准，但当前仓库找不到对应的 `feature/<slug>` worktree** → 进入阶段 2（`stages/using-git-worktrees.md`）。
4. **worktree 已就位，但 `.claude/dev-flow/<slug>/plan.md` 不存在** → 进入阶段 3（`stages/writing-plans.md`）。
5. **plan.md 存在，但任务清单中还有未完成任务，且用户已下达执行指令** → 进入阶段 4（`stages/subagent-driven-development.md`）；若用户尚未下达执行指令，展示任务清单概览后等待。
6. **任务清单全部完成** → 进入阶段 5（`stages/finishing-a-development-branch.md`）。

如果无法从现有文件判断当前所处阶段（例如 `.claude/dev-flow/` 下有多个匹配的 `<slug>`），用 `AskUserQuestion` 让用户明确指出要继续哪一条。

## 中止与例外

- 纯 bug 修复、已有精确规格的小改动、文档类改动：不必走全流程，直接处理即可。
- 任何阶段卡在 Critical 问题或需要破坏性操作（合并、删除分支、强制覆盖）时，停下来交给用户决定，不要为了推进流程而跳过确认。
