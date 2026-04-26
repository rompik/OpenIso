#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""Dialogs mixin for SkeyEditor."""

from __future__ import annotations

from openiso import __version__
from openiso.core.i18n import _t, get_current_language
from openiso.view.dialogs.about_dialog import AboutDialog
from openiso.view.dialogs.help_window import HelpWindow
from openiso.view.dialogs.keyboard_shortcuts_dialog import KeyboardShortcutsDialog
from openiso.view.dialogs.settings_dialog import SettingsDialog
from openiso.view.dialogs.sync_conflicts_dialog import SyncConflictsDialog
from openiso.view.ui_constants import update_point_colors, update_scene_colors


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
        point_colors = dialog.get_point_colors()
        update_point_colors(point_colors)

        scene_colors = dialog.get_scene_colors()
        update_scene_colors(scene_colors)

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

    def _append_terminal_message(self, message: str) -> None:
        terminal_widget = getattr(self, "terminal_widget", None)
        history_area = getattr(terminal_widget, "history_area", None)
        if history_area is not None:
            history_area.append(f"<span style='color: #6a4c00;'>{message}</span>")

    def _handle_catalog_sync_feedback(self, sync_result: dict | None) -> None:
        if not sync_result:
            return

        if sync_result.get("synced"):
            message = _t(
                "Catalog sync: +{inserted} updated {updated} conflicts {conflict} user-kept {skipped_user}"
            ).format(
                inserted=sync_result.get("inserted", 0),
                updated=sync_result.get("updated", 0),
                conflict=sync_result.get("conflict", 0),
                skipped_user=sync_result.get("skipped_user", 0),
            )
            self.status_bar_widget.showMessage(message, 8000)
            self._append_terminal_message(message)

            conflicts = self.controller.get_sync_conflicts()
            if conflicts:
                dialog = SyncConflictsDialog(
                    conflicts,
                    sync_result,
                    details_provider=self.controller.get_sync_conflict_details,
                    parent=self,
                )
                dialog.accept_upstream_requested.connect(
                    lambda skey_name, current_dialog=dialog: self._on_accept_upstream_requested(
                        current_dialog, skey_name
                    )
                )
                dialog.keep_local_requested.connect(
                    lambda skey_name, current_dialog=dialog: self._on_keep_local_requested(
                        current_dialog, skey_name
                    )
                )
                dialog.exec()
            return

        if sync_result.get("reason") == "already_synced":
            message = _t("Catalog sync skipped: already synced for release {release}").format(
                release=sync_result.get("release", __version__)
            )
            self.status_bar_widget.showMessage(message, 5000)
            self._append_terminal_message(message)

    def _refresh_after_sync_resolution(self, skey_name: str, message: str) -> None:
        self.refresh_skey_tree()
        self.status_bar_widget.showMessage(message, 5000)
        self._append_terminal_message(message)
        self.tree_skeys.select_item_by_path(None)
        self.tree_skeys.filter_items("")

        skey_data = self.controller.get_skey(skey_name)
        if skey_data:
            self.tree_skeys.select_item_by_path(
                _t(skey_data.group_key),
                _t(f"{skey_data.group_key}.{skey_data.subgroup_key}"),
                _t(f"{skey_data.group_key}.{skey_data.subgroup_key}.{skey_data.name.lower()}"),
            )

    def _on_accept_upstream_requested(self, dialog, skey_name: str) -> None:
        if self.controller.resolve_sync_conflict_accept_upstream(skey_name):
            message = _t("Accepted upstream version for {name}").format(name=skey_name)
            self._refresh_after_sync_resolution(skey_name, message)
            dialog.mark_conflict_resolved(skey_name)

    def _on_keep_local_requested(self, dialog, skey_name: str) -> None:
        if self.controller.resolve_sync_conflict_keep_local(skey_name):
            message = _t("Kept local version for {name}").format(name=skey_name)
            self._refresh_after_sync_resolution(skey_name, message)
            dialog.mark_conflict_resolved(skey_name)
