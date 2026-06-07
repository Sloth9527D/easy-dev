# ==========================================
# 0. Initialization
# ==========================================
$ProgressPreference = 'SilentlyContinue'

$gitVersion = "2.54.0"
$arch = "64-bit" # Can be changed to "arm64" or "32-bit" if needed
$downloadDir = "E:\Downloads"
$installPath = "E:\Dev\MinGit-$gitVersion"

$gitCmdPath = "$installPath\cmd"
$gitExePath = "$gitCmdPath\git.exe"

# ==========================================
# 1 & 2. Download and Extract (ZIP Archive via tar)
# ==========================================
if (Test-Path -Path $gitExePath) {
    Write-Host "`n-> MinGit $gitVersion is already installed at: $installPath" -ForegroundColor Green
}
else {
    if (-Not (Test-Path -Path $downloadDir)) { New-Item -ItemType Directory -Path $downloadDir -Force | Out-Null }
    if (-Not (Test-Path -Path $installPath)) { New-Item -ItemType Directory -Path $installPath -Force | Out-Null }

    $gitUrl = "https://github.com/git-for-windows/git/releases/download/v$($gitVersion).windows.1/MinGit-$($gitVersion)-$($arch).zip"
    $downloadPath = "$downloadDir\MinGit-$gitVersion-$arch.zip"

    Write-Host "`n1. Downloading MinGit ZIP archive..." -ForegroundColor Cyan
    if (-Not (Test-Path -Path $downloadPath)) {
        Invoke-WebRequest -Uri $gitUrl -OutFile $downloadPath
    }

    Write-Host "`n2. Extracting MinGit silently (Fast Mode using tar)..." -ForegroundColor Cyan

    # MinGit ZIP contents are placed directly into the target directory
    tar -xf $downloadPath -C $installPath

    if ($?) {
        Remove-Item -Path $downloadPath -Force
        Write-Host "-> Extraction successful and temporary ZIP cleaned!" -ForegroundColor Green
    }
    else {
        Write-Host "-> ❌ Extraction FAILED." -ForegroundColor Red
        Write-Host ""
        cmd.exe /c pause
        exit
    }
}

# ==========================================
# 3. Configure User Environment Variable (PATH)
# ==========================================
Write-Host "`n3. Configuring Environment Variables..." -ForegroundColor Cyan

$env:Path = "$gitCmdPath;" + $env:Path
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$pathUpdated = $false

if ($null -eq $userPath) { $userPath = "" }

if ($userPath -notmatch [regex]::Escape($gitCmdPath)) {
    $userPath = "$gitCmdPath;" + $userPath
    $pathUpdated = $true
}

if ($pathUpdated) {
    [Environment]::SetEnvironmentVariable("Path", $userPath, "User")
    Write-Host "-> Added MinGit to User PATH successfully." -ForegroundColor Green
}
else {
    Write-Host "-> MinGit is already in User PATH." -ForegroundColor Green
}

# ==========================================
# 4. Print Installation Information & Test
# ==========================================
Write-Host "`n4. Installation Information:" -ForegroundColor Cyan
Write-Host "-> Target Version    : MinGit $gitVersion ($arch)" -ForegroundColor Yellow
Write-Host "-> Install Directory : $installPath" -ForegroundColor Yellow
Write-Host "-> Executable Path   : $gitExePath" -ForegroundColor Yellow
Write-Host "-> Added to PATH     : $gitCmdPath" -ForegroundColor Yellow

Write-Host "`nTesting MinGit configuration:" -ForegroundColor Cyan
git --version

# ==========================================
# 5. Automatically Configure Git Commit Template
# ==========================================
Write-Host "`n5. Configuring Global Git Commit Template..." -ForegroundColor Cyan

$gitMessagePath = "$HOME\.gitmessage"
$gitMessageContent = @"
# <type>(<scope>): <subject>
# |<----  尽量限制在 50 个字符以内  ---->|
#
# <body>
# 详细描述本次修改的动机、背景以及具体的变更。
# |<----   每行尽量限制在 72 个字符以内，解释 WHY 和 WHAT，而不是 HOW   ---->|
# 
# <footer>
# 用于记录 Breaking Changes (破坏性变更) 或关闭的 Issue (例如: Fixes #123)
#
# ----------------------------------------------------------------------
# <type> 类型说明:
#   feat     : 🚀 新增功能 (Feature)
#   fix      : 🐛 修复 Bug
#   docs     : 📝 文档更新 (Documentation)
#   style    : 🎨 代码格式修改 (不影响代码运行的变动，如空格、格式化等)
#   refactor : ♻️ 代码重构 (既不是新增功能，也不是修复 Bug 的代码变动)
#   perf     : ⚡️ 性能优化 (Performance)
#   test     : ✅ 增加或修改测试用例
#   build    : 👷 构建系统或外部依赖项的更改 (如 CMake, LLVM, Cargo 等)
#   ci       : 🔧 CI 配置文件和脚本的更改 (如 GitHub Actions)
#   chore    : 杂项，其他不修改源代码或测试文件的更改
# ----------------------------------------------------------------------
"@

# 使用 UTF8 编码写入，防止中文或 Emoji 乱码
Set-Content -Path $gitMessagePath -Value $gitMessageContent -Encoding UTF8 -Force
Write-Host "-> Generated template file at: $gitMessagePath" -ForegroundColor Green

# 自动配置 Git 全局模板
try {
    git config --global commit.template $gitMessagePath
    Write-Host "-> Auto-configured global git commit.template successfully!" -ForegroundColor Green
} catch {
    Write-Host "-> ❌ Failed to configure git commit.template." -ForegroundColor Red
}

Write-Host ""
cmd.exe /c pause