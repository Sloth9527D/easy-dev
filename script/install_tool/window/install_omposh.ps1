# ====================================================================
# Oh My Posh & Cascadia Mono Font 一键全自动部署脚本
# ====================================================================

# 1. 配置临时网络代理（仅对当前运行的脚本窗口生效）
Write-Host "[1/5] 正在配置临时网络代理..." -ForegroundColor Cyan
$env:HTTP_PROXY  = "http://127.0.0.1:10808"
$env:HTTPS_PROXY = "http://127.0.0.1:10808"

# 2. 通过 winget 安装 Oh My Posh
Write-Host "[2/5] 正在通过 winget 静默安装 Oh My Posh..." -ForegroundColor Cyan
winget install JanDeDobbeleer.OhMyPosh -s winget --silent --accept-source-agreements --accept-package-agreements

# 刷新当前控制台的环境变量，确保后续可以立刻使用 oh-my-posh 命令
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# 3. 自动安装 Cascadia Mono 字体
Write-Host "[3/5] 正在下载并安装 Cascadia Mono 字体..." -ForegroundColor Cyan
if (Get-Command oh-my-posh -ErrorAction SilentlyContinue) {
    oh-my-posh font install cascadiamono
} else {
    Write-Error "Oh My Posh 安装失败或未找到命令，请检查网络代理与 winget 状态。"
    exit
}

# 4. 自动创建并配置 PowerShell $PROFILE
Write-Host "[4/5] 正在检测并配置 PowerShell 初始化脚本..." -ForegroundColor Cyan

# 目标主题路径
$ThemePath = "C:\Program Files\WindowsApps\ohmyposh.cli_29.13.1.0_x64__96v55e8n804z4\themes\tokyo.omp.json"

# 需要写入配置文件的初始化内容
$ProfileContent = @"

# >>> Oh My Posh 初始化配置 >>>
if (Get-Command oh-my-posh -ErrorAction SilentlyContinue) {
    oh-my-posh init pwsh --config "$ThemePath" | Invoke-Expression
}
# <<< Oh My Posh 初始化配置 <<<
"@

# 确保 $PROFILE 所在的文件夹存在
$ProfileDir = Split-Path -Path $PROFILE
if (!(Test-Path $ProfileDir)) {
    New-Item -ItemType Directory -Path $ProfileDir -Force | Out-Null
}

# 如果配置文件不存在，直接创建；如果存在，追加配置（避免重复写入）
if (!(Test-Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force | Out-Null
    Set-Content -Path $PROFILE -Value $ProfileContent
    Write-Host "已成功创建配置文件并写入 OMP 初始化代码。" -ForegroundColor Green
} else {
    $CurrentConfig = Get-Content -Path $PROFILE -Raw
    if ($CurrentConfig -notlike "*oh-my-posh init*") {
        Add-Content -Path $PROFILE -Value $ProfileContent
        Write-Host "已在现有配置文件末尾追加 OMP 初始化代码。" -ForegroundColor Green
    } else {
        Write-Host "检测到配置文件中已存在相关初始化代码，跳过写入。" -ForegroundColor Yellow
    }
}

# 5. 完工提示
Write-Host "====================================================" -ForegroundColor Green
Write-Host "[5/5] 部署完成！请按照以下两步操作激活最终效果：" -ForegroundColor Green
Write-Host "1. 如果看到系统弹窗提示字体安装，请点击确认。" -ForegroundColor Yellow
Write-Host "2. 打开 Windows Terminal 设置，将当前 Shell 的字体手工指定为 'CaskaydiaCove Nerd Font'。" -ForegroundColor Yellow
Write-Host "====================================================" -ForegroundColor Green