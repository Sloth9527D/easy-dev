# ==========================================
# 0. 初始化配置与变量
# ==========================================
$ProgressPreference = 'SilentlyContinue'

# 🌟 已修改为目标版本
$cmakeVersion = "4.3.2"
$downloadDir = "E:\Downloads"
# 安装路径带版本号
$installPath = "E:\Dev\CMake-$cmakeVersion"

$cmakeBinPath = "$installPath\bin"
$cmakeExePath = "$cmakeBinPath\cmake.exe"

# ==========================================
# 1 & 2. 下载并解压 (ZIP 免安装极速版 - tar)
# ==========================================
if (Test-Path -Path $cmakeExePath) {
    Write-Host "`n-> CMake $cmakeVersion is already installed at: $installPath" -ForegroundColor Green
    Write-Host "-> Skipping download and installation steps..." -ForegroundColor Yellow
} else {
    # 确保下载和安装目录存在
    if (-Not (Test-Path -Path $downloadDir)) {
        New-Item -ItemType Directory -Path $downloadDir -Force | Out-Null
    }
    if (-Not (Test-Path -Path $installPath)) {
        New-Item -ItemType Directory -Path $installPath -Force | Out-Null
    }

    $cmakeUrl = "https://github.com/Kitware/CMake/releases/download/v$cmakeVersion/cmake-$cmakeVersion-windows-x86_64.zip"
    $downloadPath = "$downloadDir\cmake-$cmakeVersion.zip"

    Write-Host "`n1. Downloading CMake ZIP archive from GitHub, please wait..." -ForegroundColor Cyan
    if (-Not (Test-Path -Path $downloadPath)) {
        Invoke-WebRequest -Uri $cmakeUrl -OutFile $downloadPath
        Write-Host "-> Download complete! File saved to: $downloadPath" -ForegroundColor Green
    } else {
        Write-Host "-> ZIP Archive already downloaded at: $downloadPath" -ForegroundColor Green
    }

    Write-Host "`n2. Extracting CMake $cmakeVersion silently in the background (Fast Mode using tar)..." -ForegroundColor Cyan

    # 准备临时解压目录
    $tempExtractPath = "$downloadDir\cmake_temp_$cmakeVersion"
    if (Test-Path -Path $tempExtractPath) {
        Remove-Item -Path $tempExtractPath -Recurse -Force
    }

    # ⚠️ 必须先创建该目录，否则 tar 的 -C 参数会报错找不到路径
    New-Item -ItemType Directory -Path $tempExtractPath | Out-Null

    # ================= 极速解压核心 (使用系统内置 tar) =================
    tar -xf $downloadPath -C $tempExtractPath
    # ===================================================================

    # 定位解压出来的内部文件夹 (通常名为 cmake-4.3.2-windows-x86_64)
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

# 检查并添加 CMake 的 bin 目录
if ($userPath -notmatch [regex]::Escape($cmakeBinPath)) {
    $userPath = "$cmakeBinPath;" + $userPath
    $pathUpdated = $true
}

# 如果有更新，则写回用户的 PATH 变量
if ($pathUpdated) {
    [Environment]::SetEnvironmentVariable("Path", $userPath, "User")
    Write-Host "-> User environment variables updated!" -ForegroundColor Green
} else {
    Write-Host "-> Environment variables are already up to date." -ForegroundColor Green
}

# ==========================================
# 4. 打印路径 (Print Paths)
# ==========================================
Write-Host "`n4. Installation Paths Configuration:" -ForegroundColor Cyan
Write-Host "-> Install Directory : $installPath" -ForegroundColor Yellow
Write-Host "-> Executable Path   : $cmakeExePath" -ForegroundColor Yellow
Write-Host "-> Added to PATH     : $cmakeBinPath" -ForegroundColor Yellow

# 添加暂停
Write-Host ""
cmd.exe /c pause