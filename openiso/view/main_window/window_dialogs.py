#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""Dialogs mixin for SkeyEditor."""

from __future__ import annotations

from openiso import __version__
from openiso.core.i18n import _t, get_current_language, setup_i18n
from openiso.view.dialogs.about_dialog import AboutDialog
from openiso.view.dialogs.help_window import HelpWindow
from openiso.view.dialogs.keyboard_shortcuts_dialog import KeyboardShortcutsDialog
from openiso.view.dialogs.settings_dialog import SettingsDialog


class DialogsMixin:
    """Mixin providing settings, help, about and keyboard-shortcuts dialogs for SkeyEditor."""

    def _on_settings_clicked(self):
        """Opens the settings dialog and handles configuration changes."""
        dialog = SettingsDialog(self)
        if dialog.exec():
            lang_code = dialog.get_selected_language()
            if lang_code != get_current_language():
                self._change_language(lang_code)

            iso_view = dialog.get_selected_isometric_view()
            self.preview_widget.set_isometric_view(iso_view)

            self._apply_color_settings(dialog)

            if hasattr(self, 'current_skey_name') and self.current_skey_name:
                self.preview_widget.update_preview(
                    self.scene.symbol_drawlist, self.origin_x, self.origin_y
                )

    def _apply_color_settings(self, dialog):
        """Apply color settings from the dialog to the application."""
        from openiso.core import constants

        point_colors = dialog.get_point_colors()
        for key, color in point_colors.items():
            constants.POINT_COLORS[key] = color

        scene_colors = dialog.get_scene_colors()
        for key, color in scene_colors.items():
            constants.SCENE_COLORS[key] = color

        self.scene.draw_grid()
        self.status_bar_widget.showMessage(_t("Color settings applied"), 3000)

    def _on_help_clicked(self):
        """Displays application help information."""
        if not hasattr(self, 'help_window') or self.help_window is None:
            self.help_window = HelpWindow(self)
        self.help_window.show()
        self.help_window.raise_()
        self.help_window.activateWindow()

    def _on_keyboard_shortcuts_clicked(self):
        """Displays the keyboard shortcuts dialog."""
        dialog = KeyboardShortcutsDialog(self)
        dialog.exec()

    def _on_about_clicked(self):
        """Displays information about the application."""
        dialog = AboutDialog(self.icons_library_path, self)
        dialog.exec()
