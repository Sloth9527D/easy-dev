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
} else {
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
    } else {
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
} else {
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

Write-Host ""
cmd.exe /c pause