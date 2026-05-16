# ==========================================
# 0. Initialization
# ==========================================
$ProgressPreference = 'SilentlyContinue'

$gitVersion = "2.45.1"
$downloadDir = "E:\Downloads"
$installPath = "E:\Dev\Git"

$gitCmdPath = "$installPath\cmd"
$gitExePath = "$gitCmdPath\git.exe"

# ==========================================
# 1 & 2. Download and Extract (Portable Version)
# ==========================================
if (Test-Path -Path $gitExePath) {
    Write-Host "`n-> Git $gitVersion is already installed at: $installPath" -ForegroundColor Green
} else {
    if (-Not (Test-Path -Path $downloadDir)) { New-Item -ItemType Directory -Path $downloadDir -Force | Out-Null }
    if (-Not (Test-Path -Path $installPath)) { New-Item -ItemType Directory -Path $installPath -Force | Out-Null }

    $gitUrl = "https://github.com/git-for-windows/git/releases/download/v$($gitVersion).windows.1/PortableGit-$($gitVersion)-64-bit.7z.exe"
    $downloadPath = "$downloadDir\PortableGit-$gitVersion.exe"

    Write-Host "`n1. Downloading Portable Git archive..." -ForegroundColor Cyan
    if (-Not (Test-Path -Path $downloadPath)) {
        Invoke-WebRequest -Uri $gitUrl -OutFile $downloadPath
    }

    Write-Host "`n2. Extracting Portable Git silently..." -ForegroundColor Cyan
    $extractArgs = "-y -o`"$installPath`""
    $extractProcess = Start-Process -FilePath $downloadPath -ArgumentList $extractArgs -Wait -NoNewWindow -PassThru

    if ($extractProcess.ExitCode -eq 0) {
        Remove-Item -Path $downloadPath -Force
        Write-Host "-> Extraction successful and temporary files cleaned!" -ForegroundColor Green
    } else {
        Write-Host "-> ❌ Extraction FAILED with Exit Code: $($extractProcess.ExitCode)" -ForegroundColor Red
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
    Write-Host "-> Added Git to User PATH successfully." -ForegroundColor Green
} else {
    Write-Host "-> Git is already in User PATH." -ForegroundColor Green
}

# ==========================================
# 4. Print Installation Information & Test
# ==========================================
Write-Host "`n4. Installation Information:" -ForegroundColor Cyan
Write-Host "-> Git Version       : $gitVersion" -ForegroundColor Yellow
Write-Host "-> Install Directory : $installPath" -ForegroundColor Yellow
Write-Host "-> Executable Path   : $gitExePath" -ForegroundColor Yellow
Write-Host "-> Added to PATH     : $gitCmdPath" -ForegroundColor Yellow

Write-Host "`nTesting Git configuration:" -ForegroundColor Cyan
git --version

Write-Host ""
cmd.exe /c pause