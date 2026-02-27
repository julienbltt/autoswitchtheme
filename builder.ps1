# ============================================================================
# Nuitka Generator - uv workflow
# ============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$MainFile,

    [string]$OutputName = "",
    [string]$IconFile = "",
    [string]$CompanyName = "",
    [string]$ProductName = "",
    [string]$Version = "0.1.0",
    [switch]$Standalone,
    [switch]$DisableConsole,
    [switch]$Execute,
    [string]$DataFiles = ""
)

function Write-Step { param($Text) Write-Host "[+] $Text" -ForegroundColor Cyan }
function Write-OK { param($Text) Write-Host "[OK] $Text" -ForegroundColor Green }
function Write-Warn { param($Text) Write-Host "[!] $Text" -ForegroundColor Yellow }

# ============================================================================
# Read dependencies from pyproject.toml
# ============================================================================
function Get-Packages {
    $packages = @()
    $mappings = @{
        'pillow'           = 'PIL'
        'websocket-client' = 'websocket'
        'obsws-python'     = 'obsws_python'
        'opencv-python'    = 'cv2'
        'scikit-learn'     = 'sklearn'
        'beautifulsoup4'   = 'bs4'
    }

    if (Test-Path "pyproject.toml") {
        $content = Get-Content "pyproject.toml" -Raw
        if ($content -match 'dependencies\s*=\s*\[([\s\S]*?)\]') {
            $matches[1] | Select-String -Pattern '"([a-zA-Z0-9_\-\.]+)' -AllMatches |
                ForEach-Object { $_.Matches } |
                ForEach-Object {
                    $pkg = $_.Groups[1].Value.ToLower()
                    if ($mappings.ContainsKey($pkg)) {
                        $packages += $mappings[$pkg]
                    } else {
                        $packages += $_.Groups[1].Value
                    }
                }
        }
    }
    return $packages | Select-Object -Unique
}

# ============================================================================
# MAIN SCRIPT
# ============================================================================

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Nuitka Generator - uv run workflow" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check uv
Write-Step "Checking environment..."
try {
    $uvVersion = (uv --version 2>&1) -join ""
    Write-OK "uv detected: $uvVersion"
} catch {
    Write-Host "[ERROR] uv not installed" -ForegroundColor Red
    exit 1
}

# Check/install Nuitka in the project
Write-Step "Checking Nuitka in dev dependencies..."
$pyproject = Get-Content "pyproject.toml" -Raw -ErrorAction SilentlyContinue
if ($pyproject -notmatch 'nuitka') {
    Write-Warn "Nuitka not found in pyproject.toml, installing..."
    uv add --dev nuitka
    Write-OK "Nuitka added to dev dependencies"
} else {
    Write-OK "Nuitka present in pyproject.toml"
}

# Synchronize dependencies
Write-Step "Synchronizing dependencies..."
uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] uv sync failed" -ForegroundColor Red
    exit 1
}
Write-OK "Dependencies synchronized"

# Check main file
if (-not (Test-Path $MainFile)) {
    Write-Host "[ERROR] File $MainFile not found" -ForegroundColor Red
    exit 1
}
Write-OK "Main file: $MainFile"

# Default output name
if (-not $OutputName) {
    $OutputName = [System.IO.Path]::GetFileNameWithoutExtension($MainFile) + ".exe"
}

# Mode
$mode = if ($Standalone) { "--standalone" } else { "--onefile" }

# Package detection
Write-Step "Detecting dependencies..."
$packages = Get-Packages
Write-OK "$($packages.Count) packages detected: $($packages -join ', ')"

# ============================================================================
# Command generation
# ============================================================================

Write-Step "Generating command..."

$cmd = @(
    "uv run python -m nuitka"    # <-- Key change: uv run instead of uvx
    $mode
    # "--mingw64"
    "--msvc=latest"
    "--lto=yes"
    "--assume-yes-for-downloads"
    "--output-filename=$OutputName"
    "--output-folder-name=$OutputName"
    "--remove-output"
    "--enable-plugin=pylint-warnings"
    "--enable-plugin=anti-bloat"
)

# Icon
if ($IconFile -and (Test-Path $IconFile)) {
    $cmd += "--windows-icon-from-ico=`"$IconFile`""
    Write-OK "Icon: $IconFile"
}

# Console
if ($DisableConsole) {
    $cmd += "--windows-console-mode=disable"
    Write-OK "Mode: GUI (no console)"
}

# Metadata
if ($CompanyName) { $cmd += "--company-name=`"$CompanyName`"" }
if ($ProductName) { $cmd += "--product-name=`"$ProductName`"" }
$cmd += "--file-version=`"$Version`""
$cmd += "--product-version=`"$Version`""

# Packages
foreach ($pkg in $packages) {
    $cmd += "--include-package=$pkg"
}

# Data files
if ($DataFiles) {
    $DataFiles -split ',' | ForEach-Object {
        $file = $_.Trim()
        if ($file) {
            if (Test-Path $file -PathType Container) {
                $cmd += "--include-data-dir=`"$file`"=`"$file`""
            } else {
                $cmd += "--include-data-file=`"$file`"=`"$file`""
            }
        }
    }
}

# Main file
$cmd += "`"$MainFile`""

# Complete command
$command = $cmd -join " "

# ============================================================================
# Save
# ============================================================================

$command | Out-File -FilePath "build.bat" -Encoding ASCII
Write-OK "Command saved: build.bat"

Write-Host ""
Write-Host "Generated command:" -ForegroundColor Yellow
Write-Host $command -ForegroundColor White
Write-Host ""

# ============================================================================
# Execution
# ============================================================================

if ($Execute) {
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host " COMPILATION IN PROGRESS..." -ForegroundColor Yellow
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host ""

    Invoke-Expression $command

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "==================================================" -ForegroundColor Green
        Write-Host " COMPILATION SUCCESSFUL!" -ForegroundColor Green
        Write-Host "==================================================" -ForegroundColor Green
        Write-OK "Executable: $OutputName"

        if (Test-Path $OutputName) {
            $sizeMB = [math]::Round((Get-Item $OutputName).Length / 1MB, 2)
            Write-OK "Size: $sizeMB MB"
        }
    } else {
        Write-Host "[ERROR] Compilation failed (code: $LASTEXITCODE)" -ForegroundColor Red
    }
} else {
    Write-Host "To compile, run:" -ForegroundColor Cyan
    Write-Host "  .\build.bat" -ForegroundColor Yellow
}

Write-Host ""
