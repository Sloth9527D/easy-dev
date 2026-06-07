# ==========================================
# 0. 初始化配置与变量
# ==========================================
$ProgressPreference = 'SilentlyContinue'

# 🌟 可在此处修改为你需要的目标版本
$nodeVersion = "24.15.0"
$downloadDir = "E:\Downloads"
# 安装路径带版本号
$installPath = "E:\Dev\Node-$nodeVersion"

# 💡 核心适配：Windows 免安装版的 node.exe 直接在根目录下，没有 bin 目录
$nodeBinPath = $installPath
$nodeExePath = "$nodeBinPath\node.exe"

$env:HTTPS_PROXY = "http://127.0.0.1:10808"
$env:HTTP_PROXY = "http://127.0.0.1:10808"

# ==========================================
# 1 & 2. 下载并解压 (ZIP 免安装极速版 - tar)
# ==========================================
if (Test-Path -Path $nodeExePath) {
    Write-Host "`n-> Node.js $nodeVersion is already installed at: $installPath" -ForegroundColor Green
    Write-Host "-> Skipping download and installation steps..." -ForegroundColor Yellow
}
else {
    # 确保下载和安装目录存在
    if (-Not (Test-Path -Path $downloadDir)) {
        New-Item -ItemType Directory -Path $downloadDir -Force | Out-Null
    }
    if (-Not (Test-Path -Path $installPath)) {
        New-Item -ItemType Directory -Path $installPath -Force | Out-Null
    }

    # 官方 Windows 64位 免安装纯净包地址
    $nodeUrl = "https://nodejs.org/dist/v$nodeVersion/node-v$nodeVersion-win-x64.zip"
    $downloadPath = "$downloadDir\node-v$nodeVersion.zip"

    Write-Host "`n1. Downloading Node.js ZIP archive from official site, please wait..." -ForegroundColor Cyan
    if (-Not (Test-Path -Path $downloadPath)) {
        Invoke-WebRequest -Uri $nodeUrl -OutFile $downloadPath
        Write-Host "-> Download complete! File saved to: $downloadPath" -ForegroundColor Green
    }
    else {
        Write-Host "-> ZIP Archive already downloaded at: $downloadPath" -ForegroundColor Green
    }

    Write-Host "`n2. Extracting Node.js $nodeVersion silently in the background (Fast Mode using tar)..." -ForegroundColor Cyan

    # 准备临时解压目录
    $tempExtractPath = "$downloadDir\node_temp_$nodeVersion"
    if (Test-Path -Path $tempExtractPath) {
        Remove-Item -Path $tempExtractPath -Recurse -Force
    }

    # ⚠️ 必须先创建该目录，否则 tar 的 -C 参数会报错找不到路径
    New-Item -ItemType Directory -Path $tempExtractPath | Out-Null

    # ================= 极速解压核心 (使用系统内置 tar) =================
    tar -xf $downloadPath -C $tempExtractPath
    # ===================================================================

    $extractedFolder = Get-ChildItem -Path $tempExtractPath -Directory | Select-Object -First 1

    # 将内部的所有文件复制到最终的安装路径
    Copy-Item -Path "$($extractedFolder.FullName)\*" -Destination $installPath -Recurse -Force

    # 🌟 自动清理垃圾文件 🌟
    Remove-Item -Path $tempExtractPath -Recurse -Force  # 清理临时解压文件夹
    Remove-Item -Path $downloadPath -Force              # 清除下载的 ZIP 压缩包
    Write-Host "-> Cleaned up temporary files and ZIP archive!" -ForegroundColor DarkGray
    Write-Host "-> Extraction and deployment successful!" -ForegroundColor Green
}

# ==========================================
# 3. 刷新并验证用户环境变量 (User Scope)
# ==========================================
Write-Host "`n3. Checking and Refreshing User Environment Variables..." -ForegroundColor Cyan
# 读取当前用户的 PATH 变量 ("User" 作用域，免管理员权限)
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$pathUpdated = $false

# 如果用户的 PATH 变量为空，先初始化为空字符串
if ($null -eq $userPath) { $userPath = "" }

# 检查并添加 Node.js 的目录 (不区分大小写正则检查)
if ($userPath -notmatch [regex]::Escape($nodeBinPath)) {
    # 💡 优化：将 Node 路径插到最前面，防止电脑里其他旧版本 Node 干扰
    $userPath = "$nodeBinPath;" + $userPath
    $pathUpdated = $true
}

# 如果有更新，则写回用户的 PATH 变量
if ($pathUpdated) {
    [Environment]::SetEnvironmentVariable("Path", $userPath, "User")
    Write-Host "-> User environment variables updated!" -ForegroundColor Green
}
else {
    Write-Host "-> Environment variables are already up to date." -ForegroundColor Green
}

# ==========================================
# 4. 打印路径 (Print Paths)
# ==========================================
Write-Host "`n4. Installation Paths Configuration:" -ForegroundColor Cyan
Write-Host "-> Install Directory : $installPath" -ForegroundColor Yellow
Write-Host "-> Executable Path   : $nodeExePath" -ForegroundColor Yellow
Write-Host "-> Added to PATH     : $nodeBinPath" -ForegroundColor Yellow

Write-Host "`n📢 Notice: Please restart your terminal window to load the new node and npm commands!" -ForegroundColor Yellow

# 添加暂停
Write-Host ""
cmd.exe /c pause