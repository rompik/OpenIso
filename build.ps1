$ErrorActionPreference = 'Stop'

$repoRoot = $PSScriptRoot
Set-Location $repoRoot

# Show version if available.
$version = ''
$versionFile = Join-Path $repoRoot 'VERSION'
if (Test-Path $versionFile) {
    $version = (Get-Content $versionFile -ErrorAction Stop | Select-Object -First 1).Trim()
    if ($version) {
        Write-Host "Building OpenIso version $version"
    }
}

$versionParts = @(0, 0, 0, 0)
$productVersion = 'dev'
$sourceExeName = 'OpenIso.exe'
if ($version) {
        if ($version -notmatch '^\d+(\.\d+){1,3}$') {
                throw "VERSION must contain 1 to 4 numeric components; got '$version'."
        }
        $versionParts = @($version.Split('.') | ForEach-Object { [int]$_ })
        while ($versionParts.Count -lt 4) {
                $versionParts += 0
        }
        $productVersion = $version
        $sourceExeName = "OpenIso_$version.exe"
}
$versionTuple = $versionParts -join ', '
$buildDate = Get-Date -Format 'yyyyMMdd'
$versionInfoPath = Join-Path ([System.IO.Path]::GetTempPath()) "OpenIso-version-info-$PID.txt"
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$versionInfo = @"
VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=($versionTuple), prodvers=($versionTuple),
        mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)
    ),
    kids=[
        StringFileInfo([
            StringTable('040904B0', [
                StringStruct('CompanyName', 'Roman PARYGIN'),
                StringStruct('FileDescription', 'Lightweight isometric piping symbol editor'),
                StringStruct('FileVersion', '$productVersion'),
                StringStruct('InternalName', 'OpenIso'),
                StringStruct('LegalCopyright', 'Copyright (c) $(Get-Date -Format yyyy) Roman PARYGIN'),
                StringStruct('OriginalFilename', '$sourceExeName'),
                StringStruct('ProductName', 'OpenIso'),
                StringStruct('ProductVersion', '$productVersion')
            ])
        ]),
        VarFileInfo([VarStruct('Translation', [1033, 1200])])
    ]
)
"@

# Clean previous build output.
foreach ($path in @('build', 'dist')) {
    $fullPath = Join-Path $repoRoot $path
    if (Test-Path $fullPath) {
        Remove-Item -Recurse -Force $fullPath
    }
}

# Install or update Python dependencies.
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to install Python dependencies.'
}

# Build with PyInstaller (clean cache).
$null = [System.IO.File]::WriteAllText($versionInfoPath, $versionInfo, $utf8NoBom)
$env:OPENISO_VERSION_INFO = $versionInfoPath
try {
    python -m PyInstaller --clean OpenIso_win.spec
    if ($LASTEXITCODE -ne 0) {
        throw 'PyInstaller failed to build OpenIso.'
    }
} finally {
    Remove-Item Env:OPENISO_VERSION_INFO -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $versionInfoPath -Force -ErrorAction SilentlyContinue
}

# Rename output EXE to include version and build date.
$versionTag = if ($version) { $version } else { 'dev' }
$exePath = Join-Path $repoRoot "dist\$sourceExeName"
if (Test-Path $exePath) {
    $newExeName = "OpenIso-$versionTag-$buildDate.exe"
    $newExePath = Join-Path (Split-Path $exePath -Parent) $newExeName
    Move-Item -Force $exePath $newExePath
    Write-Host "Renamed EXE to $newExeName"
} else {
    Write-Warning "EXE not found at $exePath"
}