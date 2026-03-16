# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Resolve repo root from spec path or cwd (works regardless of cwd)
spec_path = Path(SPECPATH).resolve()
spec_root = None

for candidate in [spec_path.parent, *spec_path.parents]:
    if (candidate / 'openiso' / '__main__.py').exists():
        spec_root = candidate
        break

if spec_root is None:
    cwd = Path.cwd().resolve()
    if (cwd / 'openiso' / '__main__.py').exists():
        spec_root = cwd
    else:
        spec_root = spec_path.parent

# Platform detection
is_windows = sys.platform == 'win32'
is_linux = sys.platform.startswith('linux')
is_mac = sys.platform == 'darwin'

# Define all data files to include
datas = [
    # Icons
    (str(spec_root / 'data' / 'icons'), 'data/icons'),

    # Settings
    (str(spec_root / 'data' / 'settings'), 'data/settings'),

    # Database files
    (str(spec_root / 'data' / 'database'), 'data/database'),

    # CSS files
    (str(spec_root / 'data' / 'markdown.css'), 'data'),
    (str(spec_root / 'data' / 'style.css'), 'data'),

    # Translation files (.mo + JSON)
    (str(spec_root / 'po' / 'en' / 'LC_MESSAGES' / 'openiso.mo'), 'po/en/LC_MESSAGES'),
    (str(spec_root / 'po' / 'ru' / 'LC_MESSAGES' / 'openiso.mo'), 'po/ru/LC_MESSAGES'),
    (str(spec_root / 'po' / 'en.json'), 'po'),
    (str(spec_root / 'po' / 'ru.json'), 'po'),

    # OpenIso source modules
    (str(spec_root / 'openiso'), 'openiso'),

    # Version file
    (str(spec_root / 'VERSION'), '.'),
]

# Hidden imports - include all PyQt6 modules and potential dependencies
hiddenimports = [
    # PyQt6 modules
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtSvg',
    'PyQt6.sip',

    # External dependencies
    'markdown',

    # Standard library modules (explicit for reliability)
    'sqlite3',
    'json',
    'xml.etree.ElementTree',
    'gettext',
    'locale',
    'pathlib',
    'glob',
    'subprocess',
]

a = Analysis(
    [str(spec_root / 'openiso' / '__main__.py')],
    pathex=[str(spec_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# Windows icon configuration
# Place your icon file as 'data/icons/openiso.ico' or update the path below
icon_path = spec_root / 'data' / 'icons' / 'openiso.ico'
icon_file = str(icon_path) if icon_path.exists() and is_windows else None

# Build mode: set OPENISO_ONEFILE=1 to produce a single executable
onefile = os.environ.get('OPENISO_ONEFILE', '').strip() in {'1', 'true', 'TRUE', 'yes', 'YES'}

# Versioned output name
version_file = spec_root / 'VERSION'
version = version_file.read_text(encoding='utf-8').strip() if version_file.exists() else ''
exe_name = f"OpenIso_{version}" if version else 'OpenIso'

# EXE configuration
exe = EXE(
    pyz,
    a.scripts,
    [] if onefile else [],
    exclude_binaries=not onefile,
    name=exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None if onefile else None,
    console=False,  # Set to True for debugging on Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,  # Windows icon
)

if onefile:
    exe.binaries = a.binaries
    exe.datas = a.datas
else:
    # One-folder distribution (default)
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name=exe_name,
    )
