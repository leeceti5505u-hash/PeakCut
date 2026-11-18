param(
    [string]$Target = (Join-Path (Resolve-Path (Join-Path $PSScriptRoot "..")).Path 'dist\PeakCut Desktop\PeakCut Desktop.exe')
)
$ErrorActionPreference = "Stop"
if (-not (Test-Path $Target)) { throw "PeakCut Desktop was not found at: $Target. Run build-windows.ps1 first." }
$desktop = [Environment]::GetFolderPath("Desktop")
$startMenu = Join-Path ([Environment]::GetFolderPath("Programs")) "PeakCut Desktop"
New-Item -ItemType Directory -Force -Path $startMenu | Out-Null
$shell = New-Object -ComObject WScript.Shell
foreach ($path in @((Join-Path $desktop "PeakCut Desktop.lnk"), (Join-Path $startMenu "PeakCut Desktop.lnk"))) {
    $shortcut = $shell.CreateShortcut($path)
    $shortcut.TargetPath = $Target
    $shortcut.WorkingDirectory = Split-Path $Target
    $shortcut.Description = "Open PeakCut Desktop"
    $shortcut.Save()
}
Write-Host "Desktop and Start Menu shortcuts created." -ForegroundColor Green
