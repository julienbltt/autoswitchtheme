# ============================================================================
# PowerShell Script - Automatic Nuitka Command Generator
# Automatic version (no interaction)
# ============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$MainFile,
    
    [string]$OutputName = "",
    [string]$IconFile = "",
    [string]$CompanyName = "",
    [string]$ProductName = "",
    [string]$Version = "1.0.0.0",
    [switch]$Standalone,
    [switch]$DisableConsole,
    [switch]$Execute,
    [string]$DataFiles = ""
)

# Functions to display messages
function Write-Step {
    param($Text)
    Write-Host "[+] $Text" -ForegroundColor Cyan
}

function Write-OK {
    param($Text)
    Write-Host "[OK] $Text" -ForegroundColor Green
}

function Write-Warn {
    param($Text)
    Write-Host "[!] $Text" -ForegroundColor Yellow
}

# ============================================================================
# Function to read requirement.txt
# ============================================================================
function Get-Packages {
    if (-not (Test-Path "requirement.txt")) {
        Write-Warn "requirement.txt not found"
        return @()
    }
    
    $packages = @()
    Get-Content "requirement.txt" | ForEach-Object {
        if ($_ -match '^([a-zA-Z0-9_\-\.]+)') {
            if ($matches[1] -ieq "pillow" -or $matches[1] -ieq "Pillow") {
                $packages += "PIL"
            }
            else {
                $packages += $matches[1]
            }
        }
    }
    return $packages
}

# ============================================================================
# MAIN SCRIPT
# ============================================================================

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Nuitka Generator - Automatic Mode" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Verifications
Write-Step "Checking environment..."
try {
    $null = python -m nuitka --version 2>&1
    Write-OK "Nuitka detected"
} catch {
    Write-Host "[ERROR] Nuitka not installed" -ForegroundColor Red
    exit 1
}

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

# Detect packages
Write-Step "Detecting dependencies..."
$packages = Get-Packages
Write-OK "$($packages.Count) packages detected"

# ============================================================================
# Command Generation
# ============================================================================

Write-Step "Generating command..."

$cmd = @(
    "python -m nuitka"
    "--mingw64"
    $mode
    "--output-filename=$OutputName"
    "--assume-yes-for-downloads"
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
if ($CompanyName) {
    $cmd += "--windows-company-name=`"$CompanyName`""
}
if ($ProductName) {
    $cmd += "--windows-product-name=`"$ProductName`""
}
$cmd += "--windows-file-version=`"$Version`""
$cmd += "--windows-product-version=`"$Version`""

# Packages
foreach ($pkg in $packages) {
    $cmd += "--include-package=$pkg"
}

# Data files
if ($DataFiles) {
    $filesList = $DataFiles -split ','
    foreach ($file in $filesList) {
        $file = $file.Trim()
        if ($file) {
            $source = ($file -split '=')[0].Trim()
            if (Test-Path $source -PathType Container) {
                $cmd += "--include-data-dir=`"$file`""
            } else {
                $cmd += "--include-data-file=`"$file`""
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

# Display
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
        Write-Host ""
        Write-OK "Executable: $OutputName"

        if (Test-Path $OutputName) {
            $sizeMB = [math]::Round((Get-Item $OutputName).Length / 1MB, 2)
            Write-OK "Size: $sizeMB MB"
        }
    } else {
        Write-Host ""
        Write-Host "[ERROR] Compilation failed (code: $LASTEXITCODE)" -ForegroundColor Red
    }
} else {
    Write-Host "To compile, run:" -ForegroundColor Cyan
    Write-Host "  .\build.bat" -ForegroundColor Yellow
}

Write-Host ""
