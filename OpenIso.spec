# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the spec file directory (project root)
spec_root = os.path.dirname(os.path.abspath(SPECPATH))

# Platform detection
is_windows = sys.platform == 'win32'
is_linux = sys.platform.startswith('linux')
is_mac = sys.platform == 'darwin'

# Define all data files to include
datas = [
    # Icons
    (os.path.join(spec_root, 'data', 'icons'), 'data/icons'),

    # Settings
    (os.path.join(spec_root, 'data', 'settings'), 'data/settings'),

    # Database files
    (os.path.join(spec_root, 'data', 'database'), 'data/database'),

    # CSS files
    (os.path.join(spec_root, 'data', 'markdown.css'), 'data'),
    (os.path.join(spec_root, 'data', 'style.css'), 'data'),

    # Translation files (.mo)
    (os.path.join(spec_root, 'po', '*.mo'), 'po'),
    (os.path.join(spec_root, 'po', 'en'), 'po/en'),
    (os.path.join(spec_root, 'po', 'ru'), 'po/ru'),

    # OpenIso source modules
    (os.path.join(spec_root, 'openiso'), 'openiso'),
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
    [os.path.join(spec_root, 'openiso', '__main__.py')],
    pathex=[spec_root],
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
icon_path = os.path.join(spec_root, 'data', 'icons', 'openiso.ico')
icon_file = icon_path if os.path.exists(icon_path) and is_windows else None

# EXE configuration
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OpenIso',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for debugging on Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,  # Windows icon
)

# One-folder distribution (default)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OpenIso',
)

# Uncomment below for one-file distribution (single executable)
# This creates a single .exe file but may be slower to start
"""
exe_onefile = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='OpenIso',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)
"""
