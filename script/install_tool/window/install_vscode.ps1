# =========================================================================
# VS Code 安装与配置右键菜单脚本
# =========================================================================

# 1. 初始化设置 (修复进度条Bug，提速下载)
$ProgressPreference = 'SilentlyContinue'
$downloadDir = "E:\Downloads"

# 检查并创建下载目录
if (-Not (Test-Path -Path $downloadDir)) {
    Write-Host "Creating download directory: $downloadDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $downloadDir | Out-Null
}

# 2. 下载 VS Code (最新 System Installer)
$vscodeUrl = "https://update.code.visualstudio.com/latest/win32-x64/stable"
$vscodePath = "$downloadDir\VSCodeSetup-x64.exe"

Write-Host "`n[1/3] Downloading the latest VS Code..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $vscodeUrl -OutFile $vscodePath
Write-Host "-> Download completed!" -ForegroundColor Green

# 3. 静默安装
Write-Host "`n[2/3] Installing VS Code silently in the background..." -ForegroundColor Cyan
# 参数解释：完全静默，并自动勾选“创建桌面快捷方式”、“添加到环境变量”
$vscodeArgs = "/verysilent /mergetasks=`"desktopicon,addtopath`""
Start-Process -FilePath $vscodePath -ArgumentList $vscodeArgs -Wait -NoNewWindow
Write-Host "-> Installation process finished!" -ForegroundColor Green


# =========================================================================
# 4. 安装后强制写入右键菜单注册表
# =========================================================================
Write-Host "`n[3/3] Forcing context menu registry configuration..." -ForegroundColor Cyan

# 自动探测刚才安装的 VS Code 实际路径 (兼容系统级和用户级)
$systemPath = "C:\Program Files\Microsoft VS Code\Code.exe"
$userPath = "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe"

$codeExe = if (Test-Path $systemPath) { $systemPath } 
elseif (Test-Path $userPath) { $userPath } 
else { $null }

if ($codeExe) {
    # 定义注册表路径 (HKCU 当前用户免管理员权限)
    $menuConfigs = @(
        # 1. 任意文件右键
        @{ Path = "HKCU:\Software\Classes\*\shell\VSCode"; Command = "`"$codeExe`" `"%1`"" },
        # 2. 文件夹右键
        @{ Path = "HKCU:\Software\Classes\Directory\shell\VSCode"; Command = "`"$codeExe`" `"%1`"" },
        # 3. 文件夹内部空白处右键
        @{ Path = "HKCU:\Software\Classes\Directory\Background\shell\VSCode"; Command = "`"$codeExe`" `"%V`"" }
    )

    # 循环强行写入
    foreach ($config in $menuConfigs) {
        $regPath = $config.Path
        $cmdPath = "$regPath\command"
        
        # 创建主菜单项
        if (-not (Test-Path $regPath)) { New-Item -Path $regPath -Force | Out-Null }
        Set-ItemProperty -Path $regPath -Name "(default)" -Value "Open with Code" -Force
        Set-ItemProperty -Path $regPath -Name "Icon" -Value $codeExe -Force
        
        # 创建执行命令项
        if (-not (Test-Path $cmdPath)) { New-Item -Path $cmdPath -Force | Out-Null }
        Set-ItemProperty -Path $cmdPath -Name "(default)" -Value $config.Command -Force
    }
    Write-Host "-> Context menu registered successfully!" -ForegroundColor Green
}
else {
    Write-Host "-> [Error] Code.exe path not found. Registry configuration failed." -ForegroundColor Red
}

# =========================================================================
Write-Host "`nAll done! You can now test the context menu on any file or folder." -ForegroundColor Yellow
Read-Host "Press Enter to exit"