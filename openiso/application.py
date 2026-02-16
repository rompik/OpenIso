#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""
Application class for OpenIso.

This module provides the main Application class that handles
application lifecycle and resource management.
"""

from typing import Optional

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

try:
    from . import __version__, __app_id__
except ImportError:
    from __init__ import __version__, __app_id__


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
        self.pkgdatadir = Path(pkgdatadir) if pkgdatadir else self._find_data_dir()

        self._qt_app = None
        self._settings = None

    def _find_data_dir(self) -> Path:
        """Find the data directory for development or installed mode."""
        # Check if running from source
        source_dir = Path(__file__).parent.parent.parent / 'data'
        if source_dir.exists():
            return source_dir

        # Check standard install locations
        for prefix in ['/usr/local', '/usr', Path.home() / '.local']:
            data_dir = Path(prefix) / 'share' / 'openiso'
            if data_dir.exists():
                return data_dir

        # Fallback to current directory
        return Path.cwd() / 'data'

    @property
    def icons_dir(self) -> Path:
        """Get the icons directory path."""
        return self.pkgdatadir / 'icons'

    @property
    def settings_dir(self) -> Path:
        """Get the settings directory path."""
        return self.pkgdatadir / 'settings'

    @property
    def database_dir(self) -> Path:
        """Get the database directory path."""
        return self.pkgdatadir / 'database'

    @property
    def settings(self) -> QSettings:
        """Get application settings."""
        if self._settings is None:
            self._settings = QSettings(
                'io.github.rompik',
                'OpenIso'
            )
        return self._settings

    def get_icon_path(self, icon_name: str) -> str:
        """
        Get full path to an icon file.

        Args:
            icon_name: Icon filename (can include subdirectory)

        Returns:
            Full path to the icon file
        """
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

        self._qt_app = QApplication(argv)
        self._qt_app.setApplicationName('OpenIso')
        self._qt_app.setApplicationVersion(self.version)
        self._qt_app.setOrganizationName('io.github.rompik')
        self._qt_app.setOrganizationDomain('github.io')
        self._qt_app.setDesktopFileName(self.app_id)

        # Import here to avoid circular imports
        from .view.window import SkeyEditor

        window = SkeyEditor(application=self)
        window.show()

        return self._qt_app.exec()


# Singleton instance
class _AppSingleton:
    instance: Optional['Application'] = None

def get_application() -> 'Application':
    """Get the application singleton instance."""
    if _AppSingleton.instance is None:
        _AppSingleton.instance = Application()
    return _AppSingleton.instance
