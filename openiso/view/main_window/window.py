#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""
Main window module for OpenIso.

This module contains the SkeyEditor main window.  All drawing, geometry I/O,
fill/hatch, dialog and canvas functionality is provided by the Mixin classes
imported below.
"""

# --- Patch sys.path for direct script execution ---
import os
import sys

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGroupBox,
    QVBoxLayout, QHBoxLayout, QGraphicsView, QWidget,
    QSizePolicy, QStatusBar, QLabel, QMessageBox,
)
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import Qt

from openiso.controller.services import SkeyService
from openiso.core.constants import SHEET_SIZE
from openiso.core.i18n import setup_i18n, get_current_language
from openiso.view.graphics.scene import SheetLayout
from openiso.view.widgets.skey_tree import SkeyTreeView
from openiso.view.widgets.properties import PropertiesWidget
from openiso.view.widgets.preview import PreviewWidget
from openiso.view.widgets.menu_toolbar import MenuToolbarWidget
from openiso.view.widgets.draw_toolbar import DrawToolbarWidget
from openiso.view.widgets.terminal import TerminalWidget
from openiso.view.popups.fill_color_popup import create_fill_color_menu
from openiso.view.popups.hatch_popup import create_hatch_menu
from openiso.view.base_classes.base_popup_menu_grouped import BasePopupMenuGrouped
from openiso import __version__
from openiso.core.parser import CommandParser

# --- Mixin imports ---
from openiso.view.main_window.window_draw_tools import DrawToolsMixin
from openiso.view.main_window.window_fill_hatch import FillHatchMixin
from openiso.view.main_window.window_geometry_io import GeometryIOMixin
from openiso.view.main_window.window_skey_ops import SkeyOpsMixin
from openiso.view.main_window.window_canvas import CanvasMixin
from openiso.view.main_window.window_dialogs import DialogsMixin

# Initialize translations
_t = setup_i18n()


class SkeyEditor(
    DrawToolsMixin,
    FillHatchMixin,
    GeometryIOMixin,
    SkeyOpsMixin,
    CanvasMixin,
    DialogsMixin,
    QMainWindow,
):
    """SkeyEditor main window."""

    def _on_tree_skey_changed(self, current, _previous=None):
        """Handles the selection change in the Skey tree, loading the selected symbol's data."""
        if not current:
            return

        if current.childCount() > 0:
            return  # group / subgroup node, not a leaf

        skey_name = current.data(0, Qt.ItemDataRole.UserRole)
        if not skey_name:
            skey_name = current.text(0)

        print(f"[debug] Tree selection changed to: {current.text(0)} (raw: {skey_name})")

        skey_data = self.skey_service.get_skey(skey_name)
        if not skey_data:
            print(f"[error] Skey not found in repository: {skey_name}")
            return

        self.scene.clear_symbol_drawlist()
        self.properties_widget.load_skey_data(skey_data)

        if skey_data.geometry:
            print(f"Loading {len(skey_data.geometry)} geometry items")
            self._load_geometry_to_scene(skey_data.geometry)
        else:
            print("No geometry data found")

        self.preview_widget.update_preview(self.scene.symbol_drawlist, self.origin_x, self.origin_y)
        print(f"Skey {skey_name} loaded successfully")

    def _on_group_changed(self, index):
        """Updates the subgroup selection list whenever the main Skey group is changed."""
        if index < 0:
            return

        group_key = (
            self.properties_widget.cb_skey_group.currentData()
            or self.properties_widget.cb_skey_group.currentText()
        )
        if not group_key:
            self.properties_widget.cb_skey_subgroup.clear()
            self.properties_widget.cb_skey_subgroup.addItem("", "")
            return

        self.properties_widget.cb_skey_subgroup.clear()
        subgroups = self.skey_service.get_subgroup_names(group_key)
        for subgroup in subgroups:
            path = f"{group_key}.{subgroup}"
            self.properties_widget.cb_skey_subgroup.addItem(_t(path), subgroup)

        model = self.properties_widget.cb_skey_subgroup.model()
        if model:
            model.sort(0)

    def __init__(self, parent=None, application=None):
        """Initializes the SkeyEditor window, sets up data paths and business logic services."""
        QMainWindow.__init__(self, parent)
        self._application = application

        self.sheet_width = SHEET_SIZE
        self.sheet_height = SHEET_SIZE
        self.origin_x = self.sheet_width / 2
        self.origin_y = self.sheet_height / 2

        self.icons_library_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'icons')
        )
        data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
        )
        print(f"Initializing with data_path: {data_path}")

        self._load_styles(data_path)

        self.skey_service = SkeyService(data_path, use_db=True)
        self.skey_service.load_descriptions()
        self.help_window = None

        self._setup_ui()
        print("Calling load_skeys to populate tree...")
        if self.skey_service.load_skeys():
            print("Successfully loaded skeys, populating tree...")
            self.refresh_skey_tree()
        else:
            print("Failed to load skeys from database")

    def _setup_ui(self):
        """Sets up the user interface components, layouts and initial widget states."""
        cw = self.centralWidget()
        if cw is not None:
            self.setCentralWidget(None)

        # --- Widgets ---
        self.tree_skeys = SkeyTreeView(self.icons_library_path)
        self.group_skeys = QGroupBox(_t("Skeys"))
        self.group_skeys.setFixedWidth(320)
        self.vbox_lay_skeys = QVBoxLayout()
        self.group_skeys.setLayout(self.vbox_lay_skeys)

        self.group_editor = QGroupBox(_t("Shape"))
        self.vbox_lay_editor = QVBoxLayout()
        self.group_editor.setLayout(self.vbox_lay_editor)
        self.hbox_lay_editor = QHBoxLayout()
        self.vbox_lay_editor.addLayout(self.hbox_lay_editor)
        self.group_editor.setMinimumSize(self.sheet_width + 140, self.sheet_height + 100)
        self.group_editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.properties_widget = PropertiesWidget(_t("Properties"), self.icons_library_path)
        self.preview_widget = PreviewWidget(_t("Preview"))
        self.menu_toolbar_widget = MenuToolbarWidget(self.icons_library_path)
        self.draw_toolbar_widget = DrawToolbarWidget(self.icons_library_path)

        self.command_parser = CommandParser(self)
        self.terminal_widget = TerminalWidget(self.command_parser)
        self.terminal_widget.setFixedHeight(150)

        # --- Scene / view ---
        self.tree_skeys.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.vbox_lay_skeys.addWidget(self.tree_skeys, stretch=1)

        self.scene = SheetLayout(self)
        self.scene.setSceneRect(-40, 0, self.sheet_width + 70, self.sheet_height)
        self.view_editor = QGraphicsView(self.scene, self)
        self.view_editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view_editor.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view_editor.setMouseTracking(True)
        self.view_editor.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view_editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        viewport = self.view_editor.viewport()
        if viewport is not None:
            viewport.installEventFilter(self)
        self.scene.symbol_changed.connect(
            lambda: self.preview_widget.update_preview(
                self.scene.symbol_drawlist, self.origin_x, self.origin_y
            )
        )

        self.hbox_lay_editor.addWidget(self.draw_toolbar_widget)
        self.hbox_lay_editor.addWidget(self.view_editor, stretch=1)

        if tuple(int(x) for x in __version__.split(".")) > (0, 9, 0):
            self.vbox_lay_editor.addWidget(self.terminal_widget)

        self.vbox_lay_right = QVBoxLayout()
        self.vbox_lay_right.addWidget(self.properties_widget)
        self.vbox_lay_right.addStretch()
        self.vbox_lay_right.addWidget(self.preview_widget)

        self.hbox_lay_main = QHBoxLayout()
        self.hbox_lay_main.addWidget(self.group_skeys, alignment=Qt.AlignmentFlag.AlignLeft)
        self.hbox_lay_main.addWidget(self.group_editor, stretch=1)
        self.hbox_lay_main.addStretch()
        self.hbox_lay_main.addLayout(self.vbox_lay_right)

        self.vbox_lay_main = QVBoxLayout()
        self.vbox_lay_main.addWidget(self.menu_toolbar_widget)
        self.vbox_lay_main.addLayout(self.hbox_lay_main)

        central_widget = QWidget()
        central_widget.setLayout(self.vbox_lay_main)
        self.setCentralWidget(central_widget)

        # --- Status bar ---
        self.status_bar_widget = QStatusBar()
        self.setStatusBar(self.status_bar_widget)
        self.status_label = QLabel(_t("Ready"))
        self.status_bar_widget.addWidget(self.status_label)

        self.primitive_coords_label = QLabel("")
        self.primitive_coords_label.setMinimumWidth(100)
        self.status_bar_widget.addWidget(self.primitive_coords_label)

        spacer = QLabel()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.status_bar_widget.addWidget(spacer)

        self.primitive_dimensions_label = QLabel("")
        self.primitive_dimensions_label.setMinimumWidth(100)
        self.status_bar_widget.addPermanentWidget(self.primitive_dimensions_label)

        # --- Signal connections ---
        self.menu_toolbar_widget.btn_settings.clicked.connect(self._on_settings_clicked)
        self.menu_toolbar_widget.btn_keyboard_shortcuts.clicked.connect(self._on_keyboard_shortcuts_clicked)
        self.menu_toolbar_widget.btn_help.clicked.connect(self._on_help_clicked)
        self.menu_toolbar_widget.btn_about.clicked.connect(self._on_about_clicked)

        self.draw_toolbar_widget.btn_plot_select_element.clicked.connect(self._on_select_tool_clicked)
        self.draw_toolbar_widget.btn_select_all.clicked.connect(self.select_all_items)
        self.draw_toolbar_widget.btn_move.clicked.connect(self._on_move_tool_clicked)
        self.draw_toolbar_widget.btn_rotate.clicked.connect(self._on_rotate_tool_clicked)
        self.draw_toolbar_widget.btn_scale.clicked.connect(self._on_scale_tool_clicked)

        # Connection points popup
        connection_types = [
            ("BW", _t("Butt Weld")), ("SW", _t("Socket Weld")), ("FL", _t("Flanged")),
            ("THD", _t("Threaded")), ("PL", _t("Plain")), ("CP", _t("Compression")),
            ("SC", _t("Screwed")), ("PE", _t("Plain End")), ("BE", _t("Beveled End")),
            ("TE", _t("Threaded End")),
        ]
        point_definitions = [
            (_t("Arrive Point"), "_on_draw_arrive_point_clicked"),
            (_t("Leave Point"), "_on_draw_leave_point_clicked"),
            (_t("Additional Point (Tee)"), "_on_draw_tee_point_clicked"),
        ]
        connection_groups = {
            title: {code: f"connections/{code.lower()}.svg" for code, _ in connection_types}
            for title, _ in point_definitions
        }
        action_by_group = {title: action for title, action in point_definitions}
        self.draw_toolbar_widget.btn_plot_connections.setMenu(
            BasePopupMenuGrouped.create_menu(
                self.draw_toolbar_widget.btn_plot_connections,
                _t("Select Connection Point Type"),
                connection_groups,
                self.icons_library_path,
                lambda group_title, code: self._on_connection_popup_selected(
                    code, action_by_group[group_title]
                ),
            )
        )

        # Spindle popup
        all_spindles = self.skey_service.get_all_spindles()
        self.properties_widget.update_spindles(all_spindles)
        spindle_groups: dict = {}
        for spindle in all_spindles:
            title = f"{spindle.group_key}/{spindle.subgroup_key}"
            spindle_groups.setdefault(title, {})[spindle.name] = f"spindles/{spindle.name}.svg"
        self.draw_toolbar_widget.btn_plot_point_spindle.setMenu(
            BasePopupMenuGrouped.create_menu(
                self.draw_toolbar_widget.btn_plot_point_spindle,
                _t("Select Spindle"),
                spindle_groups,
                self.icons_library_path,
                lambda _group, name: self._on_spindle_from_popup_selected(name),
            )
        )

        # Tool menus
        self.draw_toolbar_widget.setup_line_menu(self._on_line_tool_selected)
        self.draw_toolbar_widget.setup_shapes_menu(self._on_shape_tool_selected)

        self.draw_toolbar_widget.btn_fill_color.setMenu(
            create_fill_color_menu(self.draw_toolbar_widget.btn_fill_color, self._on_fill_color_selected)
        )
        self.draw_toolbar_widget.btn_hatch.setMenu(
            create_hatch_menu(self.draw_toolbar_widget.btn_hatch, self._on_hatch_selected)
        )
        self.draw_toolbar_widget.btn_clear_sheet.clicked.connect(self.clear_canvas)

        self.menu_toolbar_widget.btn_import.clicked.connect(self.import_external_file)
        self.menu_toolbar_widget.btn_export.clicked.connect(self.export_to_file)
        self.menu_toolbar_widget.btn_print.clicked.connect(self.print_symbol)
        self.menu_toolbar_widget.btn_save.clicked.connect(self.save_current_skey)
        self.draw_toolbar_widget.btn_undo.clicked.connect(self.undo_last_action)
        self.draw_toolbar_widget.btn_redo.clicked.connect(self.redo_next_action)
        self.menu_toolbar_widget.btn_import_from_ascii.clicked.connect(self.import_from_ascii_format)
        self.menu_toolbar_widget.btn_import_from_idf.clicked.connect(self.import_from_idf_format)

        self.properties_widget.btn_save.clicked.connect(self.save_current_skey)
        self.tree_skeys.current_item_changed.connect(self._on_tree_skey_changed)
        self.tree_skeys.create_skey_requested.connect(self._on_create_skey_requested)
        self.tree_skeys.delete_skey_requested.connect(self._on_delete_skey_requested)
        self.properties_widget.cb_skey_group.currentIndexChanged.connect(self._on_group_changed)
        self.scene.spindle_point_placed.connect(self._on_spindle_point_placed)
        self.scene.primitive_info_updated.connect(self._update_primitive_info_status)

    def _update_primitive_info_status(self, coords_str, dimensions_str):
        """Update status bar with primitive coordinates and dimensions."""
        self.primitive_coords_label.setText(coords_str)
        self.primitive_dimensions_label.setText(dimensions_str)

    def _change_language(self, lang_code):
        """Switches the application's interface language and updates all translatable UI strings."""
        global _t
        _t = setup_i18n(lang_code)

        self.setWindowTitle(_t("OpenIso - Skey Editor"))
        self.status_label.setText(_t("Ready"))
        self.group_skeys.setTitle(_t("Skeys List"))
        self.group_editor.setTitle(_t("Shape"))
        self.properties_widget.update_translations(_t)
        self.preview_widget.setTitle(_t("Preview"))
        self.menu_toolbar_widget.update_translations(_t)
        self.draw_toolbar_widget.update_translations(_t)
        self.tree_skeys.update_translations(_t)

        if self.skey_service.load_skeys():
            self.refresh_skey_tree()

    def _load_styles(self, data_path):
        """Loads global CSS styles from the data directory."""
        style_path = os.path.join(data_path, "style.css")
        if os.path.exists(style_path):
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
            except Exception as e:
                print(f"Error loading CSS: {e}")

    def refresh_skey_tree(self):
        """Rebuilds the Skey tree view from the latest service data."""
        _t = setup_i18n()
        self.skey_service.reload_groups()

        self.properties_widget.cb_skey_group.clear()
        self.properties_widget.cb_skey_group.addItem("", "")
        groups = self.skey_service.groups
        for group in groups.get_groups():
            self.properties_widget.cb_skey_group.addItem(_t(group), group)

        model = self.properties_widget.cb_skey_group.model()
        if model:
            model.sort(0)
        self.properties_widget.cb_skey_group.setCurrentIndex(0)
        self.properties_widget.cb_skey_subgroup.clear()
        self.properties_widget.cb_skey_subgroup.addItem("", "")

        self.tree_skeys.build_tree(groups, expanded=False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = SkeyEditor()
    main_window.show()
    sys.exit(app.exec())
