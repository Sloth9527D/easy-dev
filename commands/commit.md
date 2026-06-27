---
allowed-tools: PowerShell(git *)
description: 遵循 Conventional Commits 规范，智能分析代码变更并分步执行 Git 提交与推送（PowerShell 环境）
---

# 自动化 Git 提交助手

协助用户审查代码变更、规范化生成提交信息，并在 PowerShell 环境下一次性完成暂存、提交与推送。

---

## 阶段 1：并行分析工作区

同时执行以下三条命令（可合并为一次 PowerShell 调用）：

```powershell
git status; git diff; git diff --staged
```

**禁止全量暂存**：绝对不允许使用 `git add .` 或 `git add -A`。

---

## 阶段 2：一屏预览，等待唯一一次确认

基于分析结果，向用户展示以下内容，**不要分步骤反复询问**：

### 2.1 文件清单

列出两类文件：

- **已暂存**（`git diff --staged` 有内容）：直接用于提交，标注 `[已暂存]`
- **建议暂存**（`git diff` 中与本次改动相关的文件）：逐个列出路径，标注 `[建议]`

如果 `git diff` 中存在明显无关的文件（如临时测试文件、与本次主题无关的改动），将其排除并简短说明原因。

### 2.2 提交信息草稿

基于已暂存内容 + 建议暂存文件的 diff，直接起草提交信息：

**格式**：`<type>(<scope>): <subject>`

| type       | 用途                          |
| ---------- | ----------------------------- |
| `feat`     | 新增功能                      |
| `fix`      | 修复 Bug                      |
| `docs`     | 文档变更                      |
| `style`    | 代码格式（不影响逻辑）        |
| `refactor` | 重构（无新功能、无 Bug 修复） |
| `perf`     | 性能优化                      |
| `test`     | 测试用例                      |
| `build`    | 构建工具（CMake、webpack 等） |
| `ci`       | CI 脚本                       |
| `chore`    | 杂项维护                      |

**标题规则**：中文祈使句，不超过 50 字符，末尾无句号。

**正文（可选）**：中文，说明动机（WHY）和变更内容（WHAT），每行不超过 72 字符。

**尾注（可选）**：`Closes #xxx` 或 `BREAKING CHANGE: ...`。

### 2.3 征询确认

用一句话告知用户接下来将执行：暂存建议文件 → 提交 → 推送，等待用户回复 Y/确认/修改意见。

---

## 阶段 3：一次性执行

用户确认后，**连续执行以下步骤，不再等待**：

1. 逐个暂存建议文件（每个文件单独一条 `git add <路径>`）
2. 提交：

   ```powershell
   git commit -m "<subject>" [-m "<body>"] [-m "<footer>"]
   ```

   > body/footer 为空时省略对应的 `-m`，不传空字符串。

3. 推送（紧接提交，无需额外确认）：

   ```powershell
   git push -u origin (git branch --show-current)
   ```

---

## 中止条件

以下情况主动告知用户并停止：

- 工作区干净，暂存区也为空（无可提交内容）
- 用户明确拒绝或要求修改提交信息
- `git push` 失败且原因需要用户介入（无 remote、认证失败等）
