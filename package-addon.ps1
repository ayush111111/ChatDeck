# Package Anki Addon Script
# Creates both .zip and .ankiaddon files for distribution
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File package-addon.ps1
#   or simply double-click the file

param(
    [string]$AddonDir = "anki-addon",
    [string]$OutputName = "flashcard-sync"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Anki Addon Packager" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ensure we're in the script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($scriptPath) {
    Set-Location $scriptPath
}

Write-Host "Packaging: $OutputName" -ForegroundColor Green
Write-Host "Source: $AddonDir" -ForegroundColor Green
Write-Host ""

# Clean up any __pycache__ directories
Write-Host "[1/5] Cleaning __pycache__ directories..." -ForegroundColor Yellow
Get-ChildItem -Path $AddonDir -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Remove old packages if they exist
Write-Host "[2/5] Removing old packages..." -ForegroundColor Yellow
Remove-Item "$OutputName.zip" -ErrorAction SilentlyContinue
Remove-Item "$OutputName.ankiaddon" -ErrorAction SilentlyContinue

# Get all files from the addon directory
Write-Host "[3/5] Collecting addon files..." -ForegroundColor Yellow
$files = Get-ChildItem -Path $AddonDir -File

if ($files.Count -eq 0) {
    Write-Host "Error: No files found in $AddonDir" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "      Files to package:" -ForegroundColor Cyan
$files | ForEach-Object { Write-Host "        • $($_.Name)" -ForegroundColor Gray }

# Create ZIP file directly from addon directory
Write-Host "[4/5] Creating packages..." -ForegroundColor Yellow
Push-Location $AddonDir
$filePaths = Get-ChildItem -File | Select-Object -ExpandProperty Name
Compress-Archive -Path $filePaths -DestinationPath "..\$OutputName.zip" -Force
Pop-Location

# Create .ankiaddon file (copy of zip with different extension)
Copy-Item "$OutputName.zip" "$OutputName.ankiaddon" -Force

# Show results
Write-Host "[5/5] Verifying packages..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Packages created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Output files:" -ForegroundColor Cyan
Get-Item "$OutputName.zip", "$OutputName.ankiaddon" | ForEach-Object {
    $size = [math]::Round($_.Length / 1KB, 2)
    Write-Host "  * $($_.Name) - $size KB" -ForegroundColor White
}

Write-Host ""
Write-Host "Ready for distribution:" -ForegroundColor Green
Write-Host "  * Upload to GitHub releases" -ForegroundColor White
Write-Host "  * Upload .ankiaddon to AnkiWeb" -ForegroundColor White
Write-Host "  * Share .ankiaddon file directly" -ForegroundColor White
Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor Gray
Read-Host
