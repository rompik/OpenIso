$ErrorActionPreference = 'Stop'

$repoRoot = $PSScriptRoot
Set-Location $repoRoot

# Show version if available.
$versionFile = Join-Path $repoRoot 'VERSION'
if (Test-Path $versionFile) {
    $version = (Get-Content $versionFile -ErrorAction Stop | Select-Object -First 1).Trim()
    if ($version) {
        Write-Host "Building OpenIso version $version"
    }
}

# Clean previous build output.
foreach ($path in @('build', 'dist')) {
    $fullPath = Join-Path $repoRoot $path
    if (Test-Path $fullPath) {
        Remove-Item -Recurse -Force $fullPath
    }
}

# Install or update Python dependencies.
python -m pip install -r requirements.txt

# Build with PyInstaller (clean cache).
python -m PyInstaller --clean OpenIso_win.spec

# Rename output EXE to include version and build date.
$buildDate = Get-Date -Format 'yyyyMMdd'
$versionTag = if ($version) { $version } else { 'dev' }
$exePath = Join-Path $repoRoot 'dist\OpenIso\OpenIso.exe'
if (Test-Path $exePath) {
    $newExeName = "OpenIso-$versionTag-$buildDate.exe"
    $newExePath = Join-Path (Split-Path $exePath -Parent) $newExeName
    Move-Item -Force $exePath $newExePath
    Write-Host "Renamed EXE to $newExeName"
} else {
    Write-Warning "EXE not found at $exePath"
}
