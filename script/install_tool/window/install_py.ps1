# ==========================================
# 0. Fix PowerShell progress bar performance/bug
# ==========================================
$ProgressPreference = 'SilentlyContinue'

$latestVersion = "3.14.5"
$downloadDir = "E:\Downloads"
$installPath = "E:\Dev\Python\$latestVersion"
$pythonExePath = "$installPath\python.exe"

# ==========================================
# 1 & 2. 下载并安装 (含“已安装跳过”逻辑)
# ==========================================
if (Test-Path -Path $pythonExePath) {
    Write-Host "`n-> Python $latestVersion is already installed at: $installPath" -ForegroundColor Green
    Write-Host "-> Skipping download and installation steps..." -ForegroundColor Yellow
} else {
    # 创建下载目录
    if (-Not (Test-Path -Path $downloadDir)) {
        Write-Host "-> Directory not found, creating: $downloadDir" -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $downloadDir -Force | Out-Null
    }

    $pythonUrl = "https://www.python.org/ftp/python/$latestVersion/python-$latestVersion-amd64.exe"
    $downloadPath = "$downloadDir\python_install.exe"

    Write-Host "pythonUrl: $pythonUrl"
    Write-Host "downloadPath: $downloadPath"

    Write-Host "`n1. Downloading Python installer from official website, please wait..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $pythonUrl -OutFile $downloadPath
    Write-Host "-> Download complete! File saved to: $downloadPath" -ForegroundColor Green

    Write-Host "`n2. Installing Python $latestVersion silently in the background ..." -ForegroundColor Cyan
    $installArgs = "/quiet InstallAllUsers=1 Include_test=0 TargetDir=`"$installPath`""
    Start-Process -FilePath $downloadPath -ArgumentList $installArgs -Wait -NoNewWindow
    Write-Host "-> Installation successful!" -ForegroundColor Green
}

# ==========================================
# 3. 刷新并验证用户环境变量 (User Scope)
# ==========================================
Write-Host "`n3. Checking and Refreshing User Environment Variables..." -ForegroundColor Cyan
$pythonScriptsPath = "$installPath\Scripts"

# 读取当前用户的 PATH 变量 ("User" 作用域)
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$pathUpdated = $false

# 如果用户的 PATH 变量为空，先初始化为空字符串
if ($null -eq $userPath) { $userPath = "" }

# 检查并添加 Python 根目录
if ($userPath -notmatch [regex]::Escape($installPath)) {
    $userPath = "$installPath;" + $userPath
    $pathUpdated = $true
}

# 检查并添加 Python Scripts 目录 (用于 pip 等)
if ($userPath -notmatch [regex]::Escape($pythonScriptsPath)) {
    $userPath = "$pythonScriptsPath;" + $userPath
    $pathUpdated = $true
}

# 如果有更新，则写回用户的 PATH 变量
if ($pathUpdated) {
    [Environment]::SetEnvironmentVariable("Path", $userPath, "User")
    Write-Host "-> User environment variables updated!" -ForegroundColor Green
} else {
    Write-Host "-> Environment variables are already up to date." -ForegroundColor Green
}