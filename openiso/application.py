#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""
Application class for OpenIso.

This module provides the main Application class that handles
application lifecycle and resource management.
"""

import sys
import sysconfig
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import QApplication

try:
    from . import __app_id__, __version__
except ImportError:
    from __init__ import __app_id__, __version__

# Application constants (single source of truth)
APP_NAME = 'OpenIso'
ORG_NAME = 'io.github.rompik'
ORG_DOMAIN = 'github.io'


class Application:
    """
    Main application class.

    Handles application initialization, resource paths,
    and settings management.
    """

    def __init__(self, app_id: Optional[str] = None, version: Optional[str] = None, pkgdatadir: Optional[str] = None):
        """
        Initialize the application.

        Args:
            app_id: Application ID (reverse DNS notation)
            version: Application version string
            pkgdatadir: Package data directory path
        """
        self.app_id = app_id or __app_id__
        self.version = version or __version__
        self.pkgdatadir = Path(pkgdatadir) if pkgdatadir else Application._find_data_dir()

        # Pre-compute paths once to avoid repeated operations
        self.icons_dir: Path = self.pkgdatadir / 'icons'
        self.settings_dir: Path = self.pkgdatadir / 'settings'
        self.database_dir: Path = self.pkgdatadir / 'database'

        self._qt_app: Optional[QApplication] = None
        self._settings: Optional[QSettings] = None

    @staticmethod
    def _find_data_dir() -> Path:
        """Find the data directory for development or installed mode."""
        # PyInstaller bundle: data is extracted to _MEIPASS
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass is not None:
            return Path(meipass) / 'data'

        # Running from source: go up two levels from openiso/application.py
        source_dir = Path(__file__).parent.parent / 'data'
        if source_dir.exists():
            return source_dir

        # pip/venv installs with setuptools data-files
        data_root = sysconfig.get_path('data')
        if data_root:
            data_dir = Path(data_root) / 'share' / 'openiso'
            if data_dir.exists():
                return data_dir

        prefix_data_dir = Path(sys.prefix) / 'share' / 'openiso'
        if prefix_data_dir.exists():
            return prefix_data_dir

        # Standard install locations
        for prefix in ['/usr/local', '/usr', Path.home() / '.local']:
            data_dir = Path(prefix) / 'share' / 'openiso'
            if data_dir.exists():
                return data_dir

        # Fallback to current directory
        return Path.cwd() / 'data'

    @property
    def settings(self) -> QSettings:
        """Get application settings. Requires QApplication to exist."""
        if self._settings is None:
            if QApplication.instance() is None:
                raise RuntimeError("QApplication must be created before accessing settings")
            self._settings = QSettings(ORG_NAME, APP_NAME)
        return self._settings

    def get_icon_path(self, icon_name: str) -> str:
        """Get full path to an icon file as string."""
        return str(self.icons_dir / icon_name)

    def run(self, argv: Optional[list] = None) -> int:
        """
        Run the application.

        Args:
            argv: Command line arguments

        Returns:
            Application exit code
        """
        if argv is None:
            argv = sys.argv

        # Reuse existing QApplication if already created (e.g. in tests)
        existing = QApplication.instance()
        if existing is None:
            # Fix menu displacement on Windows 11 with non-integer display scaling (125%, 150%).
            # Must be called before QApplication is constructed.
            QApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )
            self._qt_app = QApplication(argv)
        else:
            self._qt_app = existing if isinstance(existing, QApplication) else QApplication(argv)
        self._qt_app.setApplicationName(APP_NAME)
        self._qt_app.setApplicationVersion(self.version)
        self._qt_app.setOrganizationName(ORG_NAME)
        self._qt_app.setOrganizationDomain(ORG_DOMAIN)
        self._qt_app.setDesktopFileName(self.app_id)

        # Register this instance as the singleton
        _set_application(self)

        # Import here to avoid circular imports
        from .view.main_window.window import SkeyEditor

        window = SkeyEditor(application=self)
        window.show()

        return self._qt_app.exec()


# Module-level singleton stored in a mutable container to avoid global statement
_singleton: dict = {'instance': None}


def _set_application(app: Application) -> None:
    """Register the active Application instance as singleton."""
    _singleton['instance'] = app


def get_application() -> Application:
    """Get the application singleton instance."""
    app = _singleton['instance']
    if app is None:
        raise RuntimeError("Application has not been initialized. Call Application.run() first.")
    return app
