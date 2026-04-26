# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""Centralized error handling for main-window UI actions."""

from __future__ import annotations

import traceback

from PyQt6.QtWidgets import QMessageBox

from openiso.core.i18n import _t


class WindowErrorHandler:
    """Helper methods to keep error-reporting out of mixins."""

    @staticmethod
    def handle_save_error(error: Exception) -> None:
        print(f"Error saving Skey: {error}")
        traceback.print_exc()

    @staticmethod
    def handle_export_error(parent, error: Exception) -> None:
        QMessageBox.critical(
            parent,
            _t("Export Error"),
            _t("Failed to export Skey: {0}").format(str(error)),
        )
        print(f"Export error: {error}")
