---
name: file2md
description: 使用 markitdown 把任意文件（PDF、Word、Excel、PPT、图片、HTML、CSV、音频等）转换为 Markdown，输出到源文件同目录。支持单个文件与批量/整目录转换；若 markitdown 未安装会自动用 pip 安装完整版。当用户想把某个文档转成 md、提取 PDF/Office 文本为 Markdown、批量转换一堆文件，或提到 markitdown 时，请使用此技能——即使用户没有明确说"转换"二字。
allowed-tools:
  - PowerShell # 检查/安装 markitdown 并执行转换
  - Read # 读取并校验转换结果
---

# 用 markitdown 把文件转成 Markdown

把 PDF、Word、Excel、PowerPoint、图片、HTML、CSV/JSON、音频等格式转换成 Markdown，转换结果默认放在**源文件同目录**下、同名 `.md` 文件（如 `report.pdf` → `report.md`）。底层用微软的 [markitdown](https://github.com/microsoft/markitdown) 命令行工具。

## 为什么这样设计

markitdown 把"读懂各种文件格式"这件麻烦事封装成了一个命令，所以这个技能的价值不在于重新实现解析，而在于**把它用对、用稳**：确保工具就绪、批量时不被单个坏文件中断、转换后核对结果是否真的有内容。输出放到源文件同目录是因为这样最符合直觉——用户转完一眼就能在原文件旁找到 md，无需记额外的输出路径。

## 命令行契约

markitdown 的用法很简单，记住这两点就够了：

- `markitdown 输入文件 -o 输出.md` —— 转换并写入指定文件（**本技能统一用这种带 `-o` 的形式**，避免 stdout 重定向在 PowerShell 下产生 UTF-16/BOM 编码问题）。
- `markitdown --version` —— 用来探测是否已安装。

支持的常见格式：PDF、`.docx`/`.pptx`/`.xlsx`、图片（含 EXIF/OCR）、音频（转写）、HTML、CSV/JSON/XML、ZIP、EPub 等。

## 操作步骤

整个流程是「确认工具就绪 → 确定要转的文件 → 逐个转换 → 核对并汇报」。

### 1. 确认 markitdown 就绪，缺失则安装

先探测，没装再装——别无条件重装，浪费时间。

```powershell
if (Get-Command markitdown -ErrorAction SilentlyContinue) {
    Write-Output "markitdown 已就绪"
} else {
    Write-Output "未检测到 markitdown，开始安装完整版…"
    pip install "markitdown[all]"
}
```

说明：

- PowerShell 下方括号必须加引号写成 `"markitdown[all]"`，否则会被当成通配符。完整版 `[all]` 带齐 PDF、Office、图片 OCR、音频转写等全部依赖，省得用户事后遇到"某格式转不了"再补装。
- 如果 `pip` 不可用或安装失败，先停下来把报错原样告诉用户（可能是没装 Python、网络/代理问题），不要反复重试。

### 2. 确定要转换的文件

根据用户给的是单个文件、多个文件，还是一个目录/通配符来决定范围：

- **单个文件**：直接用用户给的路径。
- **批量**：把目录或通配符展开成文件列表。建议只挑 markitdown 支持的扩展名，避免对一堆 `.md`/`.exe` 之类做无意义转换。

```powershell
# 示例：收集某目录下的可转换文件（按需增减扩展名）
$exts = @(".pdf",".docx",".pptx",".xlsx",".html",".htm",".csv",".json",".xml",".epub",".jpg",".png",".mp3",".wav")
$files = Get-ChildItem -Path $dir -File | Where-Object { $exts -contains $_.Extension.ToLower() }
```

### 3. 逐个转换，输出到源文件同目录

输出路径用源文件路径换扩展名为 `.md` 得到，确保落在同目录。批量时**单个文件失败不要中断整体**，记下来继续转下一个。

**单个文件：**
```powershell
$in  = "E:\docs\report.pdf"
$out = [System.IO.Path]::ChangeExtension($in, ".md")
markitdown $in -o $out
```

**批量（含容错）：**
```powershell
$ok = @(); $fail = @()
foreach ($f in $files) {
    $out = [System.IO.Path]::ChangeExtension($f.FullName, ".md")
    markitdown $f.FullName -o $out
    if ($LASTEXITCODE -eq 0 -and (Test-Path $out)) { $ok += $f.Name } else { $fail += $f.Name }
}
```

如果用户明确要求统一输出到别处（而非同目录），按用户的来：把 `$out` 改成目标目录下的同名 `.md` 即可。

### 4. 核对结果并汇报

转换可能"成功退出但内容为空"（比如扫描版 PDF 没有可提取文本）。用 Read 工具抽查生成的 `.md`：确认文件存在、非空、内容看起来合理。

然后向用户汇报：

- 成功转换了哪些文件、各自的 `.md` 路径；
- 批量时哪些失败了、失败原因（如有报错）；
- 如果某个文件转出来是空的或明显不对，提示用户——可能是扫描件需要 OCR、或该格式不被支持，不要假装成功。

## 边界与提醒

- **扫描版 PDF / 纯图片型文档**：markitdown 的离线转换提取不到文字层时结果会很空。可提示用户该文件需要 OCR，或考虑 markitdown 的 Document Intelligence 选项（`-d`，需 Azure 端点，本技能默认不用）。
- **大文件 / 音频转写**：音频转写和大文档可能较慢，属正常现象，耐心等待即可。
- **不要覆盖前不确认**：若目标 `.md` 已存在且是用户手写的内容，覆盖前先提醒。
