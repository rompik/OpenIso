#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""Skey operations mixin for SkeyEditor."""

from __future__ import annotations

import os

from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import Qt

from openiso.core.i18n import _t, get_current_language


class SkeyOpsMixin:
    """Mixin providing Skey CRUD, import and export operations for SkeyEditor."""

    # -----------------------------------------------------------------
    # Create / delete
    # -----------------------------------------------------------------

    def _on_create_skey_requested(self):
        """Prepares the editor for creating a new Skey."""
        self.properties_widget.clear_fields()
        self.scene.clear_symbol_drawlist()
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
            if self.skey_service.delete_skey(skey_name):
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
            skey_name = self.properties_widget.txt_alias_code.text().strip()
            if not skey_name:
                skey_name = self.properties_widget.txt_skey.text().strip()

            if not skey_name:
                QMessageBox.warning(self, _t("Error"), _t("Skey name cannot be empty"))
                return False

            group_key = (
                self.properties_widget.cb_skey_group.currentData()
                or self.properties_widget.cb_skey_group.currentText()
            )
            subgroup_key = (
                self.properties_widget.cb_skey_subgroup.currentData()
                or self.properties_widget.cb_skey_subgroup.currentText()
            )
            description_text = self.properties_widget.txt_skey_desc.toPlainText()
            spindle_skey = self.properties_widget.cb_spindle_skey.currentText()

            orientation = self.properties_widget.orientation_button_group.checkedId()
            flow_arrow = 2 if self.properties_widget.chk_flow_arrow.isChecked() else 1
            dimensioned = 2 if self.properties_widget.chk_dimensioned.isChecked() else 1
            tracing = 2 if self.properties_widget.chk_tracing.isChecked() else 1
            insulation = 2 if self.properties_widget.chk_insulation.isChecked() else 1

            geometry = self._collect_geometry_from_scene()

            self.skey_service.update_skey(
                name=skey_name,
                group_key=group_key,
                subgroup_key=subgroup_key,
                description_key=description_text,
                spindle_skey=spindle_skey,
                orientation=orientation,
                flow_arrow=flow_arrow,
                dimensioned=dimensioned,
                tracing=tracing,
                insulation=insulation,
                geometry=geometry,
                lang_code=get_current_language(),
            )

            self.skey_service.save_skeys()

            print(f"Reloading Skey tree after saving '{skey_name}'")
            self.refresh_skey_tree()
            self._select_skey_in_tree(skey_name)
            self.properties_widget.display_geometry(geometry)

            self.status_bar_widget.showMessage(
                _t("Skey '{0}' saved successfully").format(skey_name), 3000
            )
            print(f"Skey '{skey_name}' saved successfully")
            return True

        except Exception as e:
            print(f"Error saving Skey: {e}")
            import traceback
            traceback.print_exc()
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
                print(f"Selected Skey '{skey_name}' in tree")
                return

        print(f"Warning: Could not find Skey '{skey_name}' in tree")

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
        print("Import file clicked")

    def export_to_file(self):
        """Exports the current Skey data to an Intergraph ASCII (.asc) file."""
        skey_name = self.properties_widget.txt_skey.text().strip()
        if not skey_name:
            QMessageBox.warning(self, _t("Export Error"), _t("No Skey selected or name is empty"))
            return

        group_key = (
            self.properties_widget.cb_skey_group.currentData()
            or self.properties_widget.cb_skey_group.currentText()
        )
        subgroup_key = (
            self.properties_widget.cb_skey_subgroup.currentData()
            or self.properties_widget.cb_skey_subgroup.currentText()
        )
        description_text = self.properties_widget.txt_skey_desc.toPlainText()
        spindle_skey = self.properties_widget.cb_spindle_skey.currentText()
        orientation = self.properties_widget.orientation_button_group.checkedId()
        flow_arrow = 2 if self.properties_widget.chk_flow_arrow.isChecked() else 1
        dimensioned = 2 if self.properties_widget.chk_dimensioned.isChecked() else 1
        tracing = 2 if self.properties_widget.chk_tracing.isChecked() else 1
        insulation = 2 if self.properties_widget.chk_insulation.isChecked() else 1
        geometry = self._collect_geometry_from_scene()

        from openiso.model.skey import SkeyData

        skey = SkeyData(
            name=skey_name,
            group_key=group_key,
            subgroup_key=subgroup_key,
            description_key=description_text,
            spindle_skey=spindle_skey,
            orientation=orientation,
            flow_arrow=flow_arrow,
            dimensioned=dimensioned,
            tracing=tracing,
            insulation=insulation,
            geometry=geometry,
        )

        file_path, _ = QFileDialog.getSaveFileName(
            self, _t("Export Skey as ASCII"),
            os.path.join(os.path.expanduser("~"), f"{skey_name}.asc"),
            _t("ASCII Symbolic File") + " (*.asc);;" + _t("All Files") + " (*)",
        )
        if not file_path:
            return

        try:
            ascii_content = self.skey_service.export_skey_to_ascii(skey)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(ascii_content)
            self.status_bar_widget.showMessage(
                _t("Skey '{0}' exported to {1}").format(skey_name, os.path.basename(file_path)), 3000
            )
            print(f"Skey '{skey_name}' exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(
                self, _t("Export Error"), _t("Failed to export Skey: {0}").format(str(e))
            )
            print(f"Export error: {e}")

    def print_symbol(self):
        """Opens the printing dialog to output the current symbol design."""
        print("Print clicked")

    def import_from_ascii_format(self):
        """Executes the import process for Skey data from an ASCII-encoded text file."""
        symbol_file_path = self._show_file_open_dialog("skey")
        if symbol_file_path is None:
            return

        result = self.skey_service.import_from_ascii(symbol_file_path)
        if result.success:
            self.refresh_skey_tree()
        else:
            print(f"Import errors: {result.errors}")

    def import_from_idf_format(self):
        """Executes the import process for Skey data from an Intergraph Data File (IDF)."""
        symbol_file_path = self._show_file_open_dialog("idf")
        if symbol_file_path is None:
            return

        result = self.skey_service.import_from_idf(symbol_file_path)
        if result.success:
            self.refresh_skey_tree()
