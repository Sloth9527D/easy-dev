# ==========================================
# 0. Initialization & Auto-Fetch Latest Version
# ==========================================
$ProgressPreference = 'SilentlyContinue'

$downloadDir = "E:\Downloads"
$msvcrt = "ucrt" # Options: "ucrt" or "msvcrt"
$arch = "x86_64" # Options: "x86_64", "aarch64", "i686", "armv7"

Write-Host "Fetching the latest version information from GitHub API..." -ForegroundColor Cyan

# Fetch latest release metadata from GitHub API
$apiUrl = "https://api.github.com/repos/mstorsjo/llvm-mingw/releases/latest"
try {
    $releaseInfo = Invoke-WebRequest -Uri $apiUrl -UseBasicParsing | ConvertFrom-Json
    $llvmMingwVersion = $releaseInfo.tag_name

    # 🌟 FIXED: Removed '-download' from the pattern to match official latest naming rule
    $fileNamePattern = "llvm-mingw-$llvmMingwVersion-$msvcrt-$arch.zip"
    $asset = $releaseInfo.assets | Where-Object { $_.name -eq $fileNamePattern } | Select-Object -First 1

    if ($null -eq $asset) {
        throw "Matching asset not found for pattern: $fileNamePattern"
    }

    $llvmMingwUrl = $asset.browser_download_url
    $fileName = $asset.name
}
catch {
    Write-Host "`n[!] Failed: fetch latest release metadata from GitHub API" -ForegroundColor Red
    Write-Host "Target URL: $apiUrl" -ForegroundColor DarkGray
    Write-Host "Details   : $_" -ForegroundColor DarkGray
    Write-Host ""

    # Interactive prompt for manual fallback or termination
    $userInput = Read-Host "Please enter the version manually (e.g., 20260505) or press [Enter] to exit"

    if ([string]::IsNullOrWhiteSpace($userInput)) {
        Write-Host "-> Script terminated by user." -ForegroundColor Yellow
        Write-Host ""
        cmd.exe /c pause
        exit
    }
    else {
        $llvmMingwVersion = $userInput.Trim().TrimStart('v')
        # 🌟 FIXED: Removed '-download' from the manual fallback naming rule as well
        $fileName = "llvm-mingw-$llvmMingwVersion-$msvcrt-$arch.zip"
        $llvmMingwUrl = "https://github.com/mstorsjo/llvm-mingw/releases/download/$llvmMingwVersion/$fileName"
        Write-Host "-> Continuing with manual version: $llvmMingwVersion" -ForegroundColor Yellow
    }
}

# Define installation paths based on the determined version
$installPath = "E:\Dev\llvm-mingw-$llvmMingwVersion"
$mingwBinPath = "$installPath\bin"
$clangExePath = "$mingwBinPath\clang.exe"

# ==========================================
# 1 & 2. Download and Extract (ZIP Archive via tar)
# ==========================================
if (Test-Path -Path $clangExePath) {
    Write-Host "`n-> llvm-mingw $llvmMingwVersion is already installed at: $installPath" -ForegroundColor Green
}
else {
    if (-Not (Test-Path -Path $downloadDir)) { New-Item -ItemType Directory -Path $downloadDir -Force | Out-Null }

    $tempExtractPath = "$downloadDir\llvm_mingw_temp_$llvmMingwVersion"
    if (Test-Path -Path $tempExtractPath) { Remove-Item -Path $tempExtractPath -Recurse -Force }
    New-Item -ItemType Directory -Path $tempExtractPath | Out-Null

    $downloadPath = "$downloadDir\$fileName"

    Write-Host "`n1. Downloading llvm-mingw ZIP archive ($llvmMingwVersion)..." -ForegroundColor Cyan
    try {
        if (-Not (Test-Path -Path $downloadPath)) {
            Invoke-WebRequest -Uri $llvmMingwUrl -OutFile $downloadPath
            Write-Host "-> Download complete!" -ForegroundColor Green
        }
        else {
            Write-Host "-> Target ZIP already exists in downloads directory." -ForegroundColor Green
        }
    }
    catch {
        Write-Host "-> ❌ Download FAILED. Please check your connection or source URL:" -ForegroundColor Red
        Write-Host "   $llvmMingwUrl" -ForegroundColor DarkGray
        if (Test-Path -Path $tempExtractPath) { Remove-Item -Path $tempExtractPath -Recurse -Force }
        Write-Host ""
        cmd.exe /c pause
        exit
    }

    Write-Host "`n2. Extracting llvm-mingw silently (Fast Mode using tar)..." -ForegroundColor Cyan
    tar -xf $downloadPath -C $tempExtractPath

    if ($?) {
        $extractedFolder = Get-ChildItem -Path $tempExtractPath -Directory | Select-Object -First 1

        if (-Not (Test-Path -Path $installPath)) { New-Item -ItemType Directory -Path $installPath -Force | Out-Null }
        Copy-Item -Path "$($extractedFolder.FullName)\*" -Destination $installPath -Recurse -Force

        Remove-Item -Path $tempExtractPath -Recurse -Force
        Remove-Item -Path $downloadPath -Force
        Write-Host "-> Extraction successful and temporary files cleaned!" -ForegroundColor Green
    }
    else {
        Write-Host "-> ❌ Extraction FAILED." -ForegroundColor Red
        if (Test-Path -Path $tempExtractPath) { Remove-Item -Path $tempExtractPath -Recurse -Force }
        Write-Host ""
        cmd.exe /c pause
        exit
    }
}

# ==========================================
# 3. Configure User Environment Variable (PATH)
# ==========================================
Write-Host "`n3. Configuring Environment Variables..." -ForegroundColor Cyan

$env:Path = "$mingwBinPath;" + $env:Path
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$pathUpdated = $false

if ($null -eq $userPath) { $userPath = "" }

if ($userPath -notmatch [regex]::Escape($mingwBinPath)) {
    $userPath = "$mingwBinPath;" + $userPath
    $pathUpdated = $true
}

if ($pathUpdated) {
    [Environment]::SetEnvironmentVariable("Path", $userPath, "User")
    Write-Host "-> Added llvm-mingw to User PATH successfully." -ForegroundColor Green
}
else {
    Write-Host "-> llvm-mingw is already in User PATH." -ForegroundColor Green
}

# ==========================================
# 4. Print Installation Information & Test
# ==========================================
Write-Host "`n4. Installation Information:" -ForegroundColor Cyan
Write-Host "-> Target Version    : llvm-mingw $llvmMingwVersion ($msvcrt)" -ForegroundColor Yellow
Write-Host "-> Install Directory : $installPath" -ForegroundColor Yellow
Write-Host "-> Executable Path   : $clangExePath" -ForegroundColor Yellow
Write-Host "-> Added to PATH     : $mingwBinPath" -ForegroundColor Yellow

Write-Host "`nTesting Toolchain configuration:" -ForegroundColor Cyan
clang --version

Write-Host ""
cmd.exe /c pause