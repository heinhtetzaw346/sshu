#Requires -Version 5.1

# Set sshu version
$SSHU_VER = if ($env:SSHU_VER) { $env:SSHU_VER } else { "1.0.0" }

# Stop on any error (equivalent of set -e)
$ErrorActionPreference = "Stop"

# ── Colors / Logging ─────────────────────────────────────────────────────────

function log {
    param(
        [string]$Level,
        [string]$Message
    )
    switch ($Level) {
        "success"  { Write-Host "✔️  $Message" -ForegroundColor Green  }
        "failure"  { Write-Host "❌  $Message" -ForegroundColor Red    }
        "progress" { Write-Host "🚀  $Message" -ForegroundColor Yellow }
    }
}

# ── Admin detection ───────────────────────────────────────────────────────────

$IsAdmin = ([Security.Principal.WindowsPrincipal]
    [Security.Principal.WindowsIdentity]::GetCurrent()
).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($IsAdmin) {
    $INSTALL_PATH = "C:\Program Files\sshu"
    log progress "Administrator detected. Selecting $INSTALL_PATH as install path"
    $UPDATE_PATH = $false
} else {
    $INSTALL_PATH = "$env:LOCALAPPDATA\sshu"
    log progress "Non-administrator detected. Selecting $INSTALL_PATH as install path"
    $UPDATE_PATH = $true
}

# ── Download binary ───────────────────────────────────────────────────────────

$BINARY_NAME = "sshu-windows.exe"
$DOWNLOAD_URL = "https://github.com/heinhtetzaw346/sshu/releases/download/$SSHU_VER/$BINARY_NAME"

$TEMP_DIR = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), [System.IO.Path]::GetRandomFileName())
New-Item -ItemType Directory -Path $TEMP_DIR | Out-Null

try {
    log progress "Downloading sshu v$SSHU_VER from $DOWNLOAD_URL"
    Invoke-WebRequest -Uri $DOWNLOAD_URL -OutFile "$TEMP_DIR\sshu.exe" -UseBasicParsing

    # ── Install ───────────────────────────────────────────────────────────────

    if (-not (Test-Path $INSTALL_PATH)) {
        New-Item -ItemType Directory -Path $INSTALL_PATH | Out-Null
    }

    Move-Item -Force -Path "$TEMP_DIR\sshu.exe" -Destination "$INSTALL_PATH\sshu.exe"
    log success "Moved sshu binary to $INSTALL_PATH"

    # ── Update PATH ───────────────────────────────────────────────────────────

    if ($UPDATE_PATH) {
        $SCOPE = "User"
        $CURRENT_PATH = [Environment]::GetEnvironmentVariable("PATH", $SCOPE)

        if ($CURRENT_PATH -notlike "*$INSTALL_PATH*") {
            $NEW_PATH = "$CURRENT_PATH;$INSTALL_PATH"
            [Environment]::SetEnvironmentVariable("PATH", $NEW_PATH, $SCOPE)
            log success "Added $INSTALL_PATH to your user PATH. Restart your terminal to use sshu."
        } else {
            log progress "$INSTALL_PATH is already in PATH, skipping."
        }
    } else {
        # For system-wide installs, update machine PATH (requires admin)
        $SCOPE = "Machine"
        $CURRENT_PATH = [Environment]::GetEnvironmentVariable("PATH", $SCOPE)

        if ($CURRENT_PATH -notlike "*$INSTALL_PATH*") {
            $NEW_PATH = "$CURRENT_PATH;$INSTALL_PATH"
            [Environment]::SetEnvironmentVariable("PATH", $NEW_PATH, $SCOPE)
            log success "Added $INSTALL_PATH to system PATH."
        } else {
            log progress "$INSTALL_PATH is already in system PATH, skipping."
        }
    }

    log success "SSHU Version $SSHU_VER installed successfully"

} finally {
    # Cleanup temp dir (equivalent of trap ... EXIT)
    if (Test-Path $TEMP_DIR) {
        Remove-Item -Recurse -Force $TEMP_DIR
    }
}
