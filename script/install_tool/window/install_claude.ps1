<#
.SYNOPSIS
    配置代理、安装 Claude 客户端、配置环境变量、执行安装验证并打印汇总信息。
#>

# ==========================================
# 1. 设置网络代理 (当前会话生效)
# ==========================================
Write-Host "=> Configuring network proxy (127.0.0.1:10808)..." -ForegroundColor Cyan
$env:HTTPS_PROXY = "http://127.0.0.1:10808"
$env:HTTP_PROXY  = "http://127.0.0.1:10808"

# ==========================================
# 2. 下载并执行在线安装脚本
# ==========================================
Write-Host "=> Downloading and executing the Claude installation script..." -ForegroundColor Cyan
try {
    # 使用 Invoke-RestMethod 获取脚本内容并传递给 Invoke-Expression 执行
    Invoke-RestMethod -Uri "https://claude.ai/install.ps1" | Invoke-Expression
    Write-Host "=> Claude installation script executed successfully." -ForegroundColor Green
}
catch {
    Write-Error "Failed to download or execute the installation script. Error message: $($_.Exception.Message)"
    # 如果安装失败，则中止脚本继续向下执行
    exit
}

# ==========================================
# 3. 配置用户级环境变量 (Path)
# ==========================================
Write-Host "=> Checking and configuring environment variables..." -ForegroundColor Cyan

# 动态获取当前用户的 .local\bin 路径
$claudeExePath = "$env:USERPROFILE\.local\bin"
$pathAddedStatus = "Already Existed" # 用于记录 Path 变量的状态

# 检查预期的安装目录是否存在
if (-not (Test-Path -Path $claudeExePath)) {
    Write-Error "The expected installation path for the claude command ($claudeExePath) does not exist."
    exit
}

# 获取注册表中保存的当前用户 Path 变量
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")

# 将现有路径按照分号拆分并检查是否已经包含目标路径
if ($userPath -split ';' -notcontains $claudeExePath) {
    
    # 1. 永久写入用户环境变量
    $newPath = $userPath + ";" + $claudeExePath
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    
    # 2. 注入当前会话
    $env:Path = $env:Path + ";" + $claudeExePath
    Write-Host "=> The Path for the current terminal has been refreshed." -ForegroundColor Green
    $pathAddedStatus = "Newly Added"
}
else {
    Write-Host "=> The environment variable Path already contains $claudeExePath." -ForegroundColor Yellow
}

# ==========================================
# 4. 验证安装 (Validation)
# ==========================================
Write-Host "=> Verifying installation..." -ForegroundColor Cyan

$isInstalled = $false
$claudeVersion = "Unknown"
$executablePath = "Unknown"

try {
    # 尝试在当前环境中寻找 claude 命令
    $cmdInfo = Get-Command claude -ErrorAction Stop
    $isInstalled = $true
    $executablePath = $cmdInfo.Source
    
    Write-Host "=> Validation passed: 'claude' command is recognized." -ForegroundColor Green
    
    # 尝试获取 Claude 版本 (忽略报错，因为某些 CLI 可能不支持 --version 参数)
    $versionOutput = Invoke-Expression "claude --version" 2>$null
    if ($versionOutput) {
        $claudeVersion = $versionOutput.Trim()
    } else {
        $claudeVersion = "Installed (Version flag not supported)"
    }
}
catch {
    Write-Warning "=> Validation warning: 'claude' command is not recognized in the current session. You might need to restart your terminal."
}

# ==========================================
# 5. 打印安装信息汇总 (Print Summary)
# ==========================================
Write-Host ""
Write-Host "==================================================" -ForegroundColor Magenta
Write-Host "             INSTALLATION SUMMARY                 " -ForegroundColor Magenta
Write-Host "==================================================" -ForegroundColor Magenta
Write-Host " Proxy (HTTP/S)   : $env:HTTP_PROXY"
Write-Host " Target Directory : $claudeExePath"
Write-Host " Path Config      : $pathAddedStatus"
Write-Host " Executable Path  : $executablePath"
Write-Host " Install Status   : $(if($isInstalled){'Success'}else{'Needs Verification'})"
Write-Host " Claude Version   : $claudeVersion"
Write-Host "==================================================" -ForegroundColor Magenta
Write-Host "You can now type 'claude' in your terminal to start!" -ForegroundColor Green
Write-Host ""