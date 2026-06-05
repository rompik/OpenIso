#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""Skey operations mixin for SkeyEditor."""

from __future__ import annotations

import json
import os
import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from openiso.controller.skey_request_mapper import (
    build_save_payload,
    resolve_skey_name,
)
from openiso.core.i18n import _t, get_current_language
from openiso.view.main_window.window_error_handler import WindowErrorHandler


logger = logging.getLogger(__name__)


class SkeyOpsMixin:
    """Mixin providing Skey CRUD, import and export operations for SkeyEditor."""

    # -----------------------------------------------------------------
    # Create / delete
    # -----------------------------------------------------------------

    def _on_create_skey_requested(self):
        """Prepares the editor for creating a new Skey."""
        self._is_creating_new_skey = True
        self.current_skey_data = None
        self.properties_widget.clear_fields()
        self.scene.clear_symbol_drawlist()
        if hasattr(self, "_set_save_button_dirty"):
            self._set_save_button_dirty(True)
        if hasattr(self, "_update_all_previews"):
            self._update_all_previews()
        else:
            self.preview_widget.update_preview([], self.origin_x, self.origin_y)
        self.status_bar_widget.showMessage(_t("Create new Skey"), 3000)

    def _on_delete_skey_requested(self, skey_name: str):
        """Deletes the specified Skey after confirmation."""
        current_item = self.tree_skeys.tree.currentItem()
        target_path = None

        if current_item and current_item.text(0) == skey_name:
            parent = current_item.parent()
            if parent and parent.parent():
                subgroup_name = parent.text(0)
                grandparent = parent.parent()
                group_name = grandparent.text(0) if grandparent else None

                if grandparent and grandparent.parent():
                    index = parent.indexOfChild(current_item)
                    if parent.childCount() > 1:
                        neighbor_index = index + 1 if index < parent.childCount() - 1 else index - 1
                        neighbor_item = parent.child(neighbor_index)
                        if neighbor_item:
                            target_path = {
                                'group': group_name,
                                'subgroup': subgroup_name,
                                'skey': neighbor_item.text(0),
                            }
                    else:
                        target_path = {
                            'group': group_name,
                            'subgroup': subgroup_name,
                            'skey': None,
                        }

        reply = QMessageBox.question(
            self, _t("Delete Skey"),
            _t("Are you sure you want to delete Skey '{0}'?").format(skey_name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.controller.delete_skey(skey_name):
                self.refresh_skey_tree()

                if target_path:
                    self.tree_skeys.select_item_by_path(
                        target_path['group'],
                        target_path['subgroup'],
                        target_path['skey'],
                    )

                self.status_bar_widget.showMessage(_t("Skey '{0}' deleted").format(skey_name), 3000)
                if self.properties_widget.txt_skey.text() == skey_name:
                    if not target_path or not target_path['skey']:
                        self._on_create_skey_requested()
            else:
                QMessageBox.critical(
                    self, _t("Error"), _t("Failed to delete Skey '{0}'").format(skey_name)
                )

    # -----------------------------------------------------------------
    # Save
    # -----------------------------------------------------------------

    def save_current_skey(self):
        """Gathers form data and scene geometry, then saves the Skey to the database."""
        try:
            form_data = self.form_adapter.collect_save_form_data()
            skey_name = resolve_skey_name(form_data["alias_code"], form_data["skey_name"])

            if not skey_name:
                QMessageBox.warning(self, _t("Error"), _t("Skey name cannot be empty"))
                return False

            geometry = self._collect_geometry_from_scene()
            save_payload = build_save_payload(
                form_data,
                skey_name=skey_name,
                geometry=geometry,
                lang_code=get_current_language(),
            )

            self.controller.save_skey(**save_payload)

            logger.debug("Reloading Skey tree after saving '%s'", skey_name)
            self.refresh_skey_tree()
            self._select_skey_in_tree(skey_name)
            self.properties_widget.display_geometry(geometry)

            self.status_bar_widget.showMessage(
                _t("Skey '{0}' saved successfully").format(skey_name), 3000
            )
            self._is_creating_new_skey = False
            if hasattr(self, "_set_save_button_dirty"):
                self._set_save_button_dirty(False)
            logger.info("Skey '%s' saved successfully", skey_name)
            return True

        except (RuntimeError, ValueError, TypeError, OSError) as e:
            WindowErrorHandler.handle_save_error(e)
            return False

    def _select_skey_in_tree(self, skey_name: str):
        """Searches for and programmatically selects a specific Skey item in the tree."""
        root = self.tree_skeys.invisibleRootItem()
        if root is None:
            return

        def find_item(item, target_name):
            item_raw_name = item.data(0, Qt.ItemDataRole.UserRole)
            if (item_raw_name == target_name or item.text(0) == target_name) and item.childCount() == 0:
                return item
            for i in range(item.childCount()):
                result = find_item(item.child(i), target_name)
                if result:
                    return result
            return None

        for i in range(root.childCount()):
            item = find_item(root.child(i), skey_name)
            if item:
                self.tree_skeys.setCurrentItem(item)
                logger.debug("Selected Skey '%s' in tree", skey_name)
                return

            logger.warning("Could not find Skey '%s' in tree", skey_name)

    # -----------------------------------------------------------------
    # Import / export
    # -----------------------------------------------------------------

    def _show_file_open_dialog(self, extension: str) -> str | None:
        """Opens a native file dialog to select a file with the given extension."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, _t("Select File"),
            os.path.expanduser("~"),
            _t("Symbols file") + f" (*.{extension})",
        )
        return file_path if file_path else None

    def import_external_file(self):
        """Placeholder for importing symbol data from a generic external file."""
        logger.info("Import file clicked")

    def export_to_file(self):
        """Export either current Skey as ASCII (.asc) or full DB snapshot as OIS (.ois)."""
        form_data = self.form_adapter.collect_export_form_data()
        skey_name = form_data.get("skey_name") or "openiso_skeys"
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, _t("Export File"),
            os.path.join(os.path.expanduser("~"), f"{skey_name}.asc"),
            _t("ASCII Symbolic File") + " (*.asc);;"
            + _t("OpenIso Skey File") + " (*.ois);;"
            + _t("All Files") + " (*)",
        )
        if not file_path:
            return

        try:
            export_path = file_path
            ext = os.path.splitext(file_path)[1].lower()

            export_kind = None
            if ext == ".ois":
                export_kind = "ois"
            elif ext == ".asc":
                export_kind = "asc"
            elif ext == "":
                if "*.ois" in selected_filter:
                    export_kind = "ois"
                    export_path = file_path + ".ois"
                else:
                    export_kind = "asc"
                    export_path = file_path + ".asc"
            else:
                QMessageBox.warning(self, _t("Export Error"), _t("Unsupported export format"))
                return

            if export_kind == "ois":
                payload = self.controller.export_all_skeys_to_ois_payload()
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
                self.status_bar_widget.showMessage(
                    _t("Skeys exported to {0}").format(os.path.basename(export_path)), 3000
                )
                logger.info("All skeys exported to OIS: %s", export_path)
                return

            ascii_content = self.controller.export_all_skeys_to_ascii()
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(ascii_content)
            self.status_bar_widget.showMessage(
                _t("Skeys exported to {0}").format(os.path.basename(export_path)), 3000
            )
            logger.info("All skeys exported to ASCII: %s", export_path)
        except (RuntimeError, ValueError, TypeError, OSError) as e:
            WindowErrorHandler.handle_export_error(self, e)

    def print_symbol(self):
        """Opens the printing dialog to output the current symbol design."""
        logger.info("Print clicked")

    def import_from_ascii_format(self):
        """Executes the import process for Skey data from an ASCII-encoded text file."""
        symbol_file_path = self._show_file_open_dialog("skey")
        if symbol_file_path is None:
            return

        result = self.controller.import_from_ascii(symbol_file_path)
        if result.success:
            self.refresh_skey_tree()
        else:
            logger.warning("Import errors: %s", result.errors)

    def import_from_idf_format(self):
        """Executes the import process for Skey data from an Intergraph Data File (IDF)."""
        symbol_file_path = self._show_file_open_dialog("idf")
        if symbol_file_path is None:
            return

        result = self.controller.import_from_idf(symbol_file_path)
        if result.success:
            self.refresh_skey_tree()
