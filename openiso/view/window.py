#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""
Main window module for OpenIso.

This module contains the SkeyEditor main window and all UI components
for the symbol editor.
"""

# --- Patch sys.path for direct script execution ---
import os
import sys
if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (
    QGraphicsLineItem, QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsPathItem, QApplication, QMainWindow, QGroupBox,
    QVBoxLayout, QHBoxLayout, QFileDialog, QGraphicsView, QWidget,
    QSizePolicy, QStatusBar, QLabel, QGraphicsItem, QMessageBox, QInputDialog
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QCursor, QBrush, QPolygonF
)
from PyQt6.QtCore import Qt, QPointF
from openiso.controller.services import SkeyService
from openiso.core.constants import (
    SHEET_SIZE
)
from openiso.core.i18n import setup_i18n, get_current_language
from openiso.view.geometry_items import (
    ArrivePoint, LeavePoint, TeePoint, SpindlePoint, PointItem
)
from openiso.view.scene import SheetLayout
from openiso.view.skey_tree import SkeyTreeView
from openiso.view.properties import PropertiesWidget
from openiso.view.preview import PreviewWidget
from openiso.view.menu_toolbar import MenuToolbarWidget
from openiso.view.draw_toolbar import DrawToolbarWidget
from openiso.view.settings_dialog import SettingsDialog
from openiso.view.help_window import HelpWindow
from openiso.view.about_dialog import AboutDialog
from openiso.view.keyboard_shortcuts_dialog import KeyboardShortcutsDialog
from openiso.view.terminal import TerminalWidget
from openiso.view.fill_color_popup import create_fill_color_menu
from openiso.view.hatch_popup import create_hatch_menu
from openiso.view.base_classes.base_popup_menu_grouped import BasePopupMenuGrouped
from openiso import __version__
from openiso.core.parser import CommandParser

# Initialize translations
_t = setup_i18n()
current_language_code = get_current_language()

class SkeyEditor(QMainWindow):
    """SkeyEditor Window"""

    def _on_tree_skey_changed(self, current, _previous=None):
        """Handles the selection change in the Skey tree, loading and displaying the selected symbol's data."""
        if not current:
            return

        # Get the skey name from the selected item
        # Check if this is a leaf item (skey) and not a group/subgroup
        if current.childCount() > 0:
            # This is a group or subgroup, not a skey
            return

        # Retrieve raw skey name from UserRole
        skey_name = current.data(0, Qt.ItemDataRole.UserRole)
        # Fallback to text if data is not set
        if not skey_name:
            skey_name = current.text(0)

        print(f"[debug] Tree selection changed to: {current.text(0)} (raw: {skey_name})")

        # Get skey data from service
        skey_data = self.skey_service.get_skey(skey_name)
        if not skey_data:
            print(f"[error] Skey not found in repository: {skey_name}")
            return

        #print(f"[debug] Loaded SkeyData for: {skey_data.name}, geometry count: {len(skey_data.geometry)}")

        # Clear the scene
        self.scene.clear_symbol_drawlist()

        # Load properties into the form
        self.properties_widget.load_skey_data(skey_data)

        # Load geometry
        if skey_data.geometry:
            print(f"Loading {len(skey_data.geometry)} geometry items")
            self._load_geometry_to_scene(skey_data.geometry)
        else:
            print("No geometry data found")

        # Update preview
        self.preview_widget.update_preview(self.scene.symbol_drawlist, self.origin_x, self.origin_y)

        print(f"Skey {skey_name} loaded successfully")

    def _on_group_changed(self, index):
        """Updates the subgroup selection list whenever the main Skey group is changed in the properties."""
        if index < 0:
            return

        group_key = self.properties_widget.cb_skey_group.currentData() or self.properties_widget.cb_skey_group.currentText()
        if not group_key:
            self.properties_widget.cb_skey_subgroup.clear()
            self.properties_widget.cb_skey_subgroup.addItem("", "")
            return

        # Update subgroup combobox
        self.properties_widget.cb_skey_subgroup.clear()
        subgroups = self.skey_service.get_subgroup_names(group_key)
        for subgroup in subgroups:
            # Fix: use hierarchical path for translation
            path = f"{group_key}.{subgroup}"
            self.properties_widget.cb_skey_subgroup.addItem(_t(path), subgroup)

        # Sort subgroups
        model = self.properties_widget.cb_skey_subgroup.model()
        if model:
            model.sort(0)

    def _on_draw_rect_clicked(self):
        """Activates the tool to draw a centered rectangle on the canvas."""
        self._set_draw_action("draw_rect")

    def _on_draw_square_clicked(self):
        """Activates the tool to draw a square on the canvas."""
        self._set_draw_action("draw_square")

    def _on_draw_circle_clicked(self):
        """Activates the tool to draw a circle on the canvas."""
        self._set_draw_action("draw_circle")

    def _on_draw_diamond_clicked(self):
        """Activates the tool to draw a diamond on the canvas."""
        self._set_draw_action("draw_diamond")

    def _on_draw_triangle_clicked(self):
        """Activates the tool to draw a triangle on the canvas."""
        self._set_draw_action("draw_triangle")

    def _on_draw_cap_clicked(self):
        """Activates the tool to draw a cap on the canvas."""
        self._set_draw_action("draw_cap")

    def _on_draw_hexagon_clicked(self):
        """Activates the tool to draw a hexagon on the canvas."""
        self._set_draw_action("draw_hexagon")

    def _on_draw_pentagon_clicked(self):
        """Activates the tool to draw a pentagon on the canvas."""
        self._set_draw_action("draw_pentagon")

    def _on_draw_octagon_clicked(self):
        """Activates the tool to draw an octagon on the canvas."""
        self._set_draw_action("draw_octagon")

    def _on_draw_dodecagon_clicked(self):
        """Activates the tool to draw a dodecagon on the canvas."""
        self._set_draw_action("draw_dodecagon")

    def _on_line_tool_selected(self, category, tool_name):
        """Handle line tool selection from grouped popup menu.

        Args:
            category: Group name (e.g., "Lines")
            tool_name: Selected tool name (e.g., "Line", "Polyline", etc.)
        """
        tool_map = {
            "Line": self._on_draw_line_clicked,
            "Polyline": self._on_draw_polyline_clicked,
            "Orthogonal Polyline": self._on_draw_polyline_orthogonal_clicked
        }

        handler = tool_map.get(tool_name)
        if handler:
            handler()
        else:
            print(f"[warning] Unknown line tool: {tool_name}")

    def _on_shape_tool_selected(self, category, tool_name):
        """Handle shape tool selection from grouped popup menu.

        Args:
            category: Group name (e.g., "Basic Shapes", "Special Shapes")
            tool_name: Selected tool name (e.g., "Square", "Circle", etc.)
        """
        tool_map = {
            "Square": self._on_draw_square_clicked,
            "Rectangle": self._on_draw_rect_clicked,
            "Circle": self._on_draw_circle_clicked,
            "Triangle": self._on_draw_triangle_clicked,
            "Diamond": self._on_draw_diamond_clicked,
            "Cap": self._on_draw_cap_clicked,
            "Hexagon": self._on_draw_hexagon_clicked,
            "Pentagon": self._on_draw_pentagon_clicked,
            "Octagon": self._on_draw_octagon_clicked,
            "Dodecagon": self._on_draw_dodecagon_clicked
        }

        handler = tool_map.get(tool_name)
        if handler:
            handler()
        else:
            print(f"[warning] Unknown shape tool: {tool_name}")

    def _on_fill_color_selected(self, color):
        """Applies the selected fill color to all chosen closed primitives."""
        selected_items = self.scene.selectedItems()
        if not selected_items:
            self.status_bar_widget.showMessage(_t("No items selected to fill"), 3000)
            return

        for item in selected_items:
            if isinstance(item, (QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsPathItem)):
                item.setBrush(QBrush(color, Qt.BrushStyle.SolidPattern))

        self.status_bar_widget.showMessage(_t("Fill color applied"), 3000)

    def _on_hatch_selected(self, name, angle_or_pattern, spacing):
        """Applies the selected hatch pattern to all chosen closed primitives."""
        selected_items = self.scene.selectedItems()
        if not selected_items:
            self.status_bar_widget.showMessage(_t("No items selected for hatching"), 3000)
            return

        if name == "None":
            # Clear hatching (set to no brush)
            for item in selected_items:
                if isinstance(item, (QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsPathItem)):
                    item.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            self.status_bar_widget.showMessage(_t("Hatch cleared"), 3000)
            return

        # Apply hatch pattern
        for item in selected_items:
            if isinstance(item, (QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsPathItem)):
                brush = self._create_hatch_brush(angle_or_pattern, spacing)
                item.setBrush(brush)

        self.status_bar_widget.showMessage(_t(f"Hatch pattern '{name}' applied"), 3000)

    def _create_hatch_brush(self, angle_or_pattern, spacing):
        """Create a brush with the specified hatch pattern."""
        from PyQt6.QtGui import QPixmap, QPainter, QBrush
        from PyQt6.QtCore import Qt

        # Create a pixmap for the pattern
        size = max(spacing * 4, 32)  # Make pattern large enough
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        pen = QPen(Qt.GlobalColor.black, 1)
        painter.setPen(pen)

        if isinstance(angle_or_pattern, int):
            # Simple line pattern at an angle
            self._draw_hatch_lines(painter, size, size, angle_or_pattern, spacing)
        elif angle_or_pattern == "cross":
            # Horizontal + Vertical cross
            self._draw_hatch_lines(painter, size, size, 0, spacing)
            self._draw_hatch_lines(painter, size, size, 90, spacing)
        elif angle_or_pattern == "cross_diagonal":
            # Diagonal cross (X pattern)
            self._draw_hatch_lines(painter, size, size, 45, spacing)
            self._draw_hatch_lines(painter, size, size, 135, spacing)
        elif angle_or_pattern == "brick":
            # Brick pattern
            self._draw_brick_hatch(painter, size, size, spacing)
        elif angle_or_pattern == "dots":
            # Dot pattern
            self._draw_dot_hatch(painter, size, size, spacing)

        painter.end()
        return QBrush(pixmap)

    def _draw_hatch_lines(self, painter, width, height, angle, spacing):
        """Draw parallel lines at given angle for hatch pattern."""
        import math

        if angle == 0:
            # Horizontal lines
            y = 0
            while y < height:
                painter.drawLine(0, int(y), width, int(y))
                y += spacing
        elif angle == 90:
            # Vertical lines
            x = 0
            while x < width:
                painter.drawLine(int(x), 0, int(x), height)
                x += spacing
        elif angle == 45:
            # Diagonal lines (/)
            start = -width
            while start < width + height:
                painter.drawLine(0, int(start), int(min(start, width)), 0)
                painter.drawLine(int(max(0, start - height)), height, width, int(max(0, width + height - start)))
                start += spacing
        elif angle == 135:
            # Diagonal lines (\)
            start = 0
            while start < width + height:
                painter.drawLine(0, int(min(start, height)), int(min(start, width)), 0)
                painter.drawLine(int(max(0, start - height)), height, width, int(max(0, width + height - start)))
                start += spacing

    def _draw_brick_hatch(self, painter, width, height, spacing):
        """Draw brick-like hatch pattern."""
        y = 0
        offset = False
        while y < height:
            # Horizontal line
            painter.drawLine(0, int(y), width, int(y))

            # Vertical lines
            x = spacing // 2 if offset else 0
            while x < width:
                painter.drawLine(int(x), int(y), int(x), int(min(y + spacing, height)))
                x += spacing

            y += spacing
            offset = not offset

    def _draw_dot_hatch(self, painter, width, height, spacing):
        """Draw dot hatch pattern."""
        y = spacing // 2
        row = 0
        while y < height:
            x = spacing // 2 if row % 2 == 0 else spacing
            while x < width:
                painter.drawEllipse(int(x) - 1, int(y) - 1, 2, 2)
                x += spacing
            y += spacing
            row += 1

    def _on_spindle_from_popup_selected(self, spindle_name):
        """Callback for spindle selection from the popup menu."""
        print(f"Spindle selected from popup: {spindle_name}")
        self.scene.last_selected_spindle = spindle_name
        self._on_draw_spindle_point_clicked()
        self.status_bar_widget.showMessage(_t("Spindle selected: {name}").format(name=spindle_name), 3000)

    def _on_connection_popup_selected(self, connection_type, action):
        """Callback for connection type selection from the popup menu."""
        print(f"[debug] Connection selected: type={connection_type}, action/method={action}")
        self.scene.last_selected_connection_type = connection_type

        # 1. Try to call a method if 'action' refers to a method name (e.g., _on_draw_..._clicked)
        if hasattr(self, action):
            method = getattr(self, action)
            if callable(method):
                method()
                print(f"[debug] Called method: {action}")
            else:
                print(f"[error] Symbol '{action}' is not callable")
        # 2. Fallback: if 'action' is a direct drawing action string (e.g., draw_arrive_point)
        elif action.startswith("draw_"):
            self._set_draw_action(action)
            print(f"[debug] Fallback: Set draw action to {action}")
        else:
            print(f"[error] Unknown action or method: {action}")

        self.status_bar_widget.showMessage(_t("Connection point: {0} ({1})").format(_t(connection_type), connection_type), 3000)

    def __init__(self, parent=None, application=None):
        """Initializes the SkeyEditor window, sets up data paths, and business logic services."""
        QMainWindow.__init__(self, parent)
        self._application = application

        self.sheet_width = SHEET_SIZE
        self.sheet_height = SHEET_SIZE

        self.origin_x = self.sheet_width / 2
        self.origin_y = self.sheet_height / 2

        # Determine data paths based on application context
        # Always resolve icons path relative to project root
        self.icons_library_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'icons'))
        # Always use the absolute path to the data directory
        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
        print(f"Initializing with data_path: {data_path}")

        # Load global styles
        self._load_styles(data_path)

        # Initialize business logic service
        self.skey_service = SkeyService(data_path, use_db=True)
        self.skey_service.load_descriptions()
        self.help_window = None

        self._setup_ui()
        # Ensure Skey list is loaded on first form show
        print("Calling load_skeys to populate tree...")
        if self.skey_service.load_skeys():
            print("Successfully loaded skeys, populating tree...")
            self.refresh_skey_tree()
        else:
            print("Failed to load skeys from database")

    def _setup_ui(self):
        """Sets up the user interface components, layouts, and initial widget states."""
        # Remove old widgets/layouts if reloading
        cw = self.centralWidget()
        if cw is not None:
            self.setCentralWidget(None)

        # --- Widget creation (all widgets defined before use) ---
        self.tree_skeys = SkeyTreeView(self.icons_library_path)
        self.group_skeys = QGroupBox(_t("Skeys"))
        self.group_skeys.setFixedWidth(320)  # Set fixed width for Skeys group
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

        # --- Terminal ---
        self.command_parser = CommandParser(self)
        self.terminal_widget = TerminalWidget(self.command_parser)
        self.terminal_widget.setFixedHeight(150)

        # --- Layouts ---
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

        if __version__ > "0.9.0":
            self.vbox_lay_editor.addWidget(self.terminal_widget)

        self.vbox_lay_right = QVBoxLayout()
        self.vbox_lay_right.addWidget(self.properties_widget)
        self.vbox_lay_right.addStretch()
        self.vbox_lay_right.addWidget(self.preview_widget)


        self.hbox_lay_main = QHBoxLayout()
        self.hbox_lay_main.addWidget(self.group_skeys, alignment=Qt.AlignmentFlag.AlignLeft)
        self.hbox_lay_main.addWidget(self.group_editor, stretch=1)
        self.hbox_lay_main.addStretch()  # Push Properties group to the right
        self.hbox_lay_main.addLayout(self.vbox_lay_right)

        self.vbox_lay_main = QVBoxLayout()
        self.vbox_lay_main.addWidget(self.menu_toolbar_widget)
        self.vbox_lay_main.addLayout(self.hbox_lay_main)

        central_widget = QWidget()
        central_widget.setLayout(self.vbox_lay_main)
        self.setCentralWidget(central_widget)

        # --- Status Bar ---
        self.status_bar_widget = QStatusBar()
        self.setStatusBar(self.status_bar_widget)
        self.status_label = QLabel(_t("Ready"))
        self.status_bar_widget.addWidget(self.status_label)

        # Add primitive coordinates label (left)
        self.primitive_coords_label = QLabel("")
        self.primitive_coords_label.setMinimumWidth(100)
        self.status_bar_widget.addWidget(self.primitive_coords_label)

        # Add spacer
        spacer = QLabel()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.status_bar_widget.addWidget(spacer)

        # Add primitive dimensions label (right)
        self.primitive_dimensions_label = QLabel("")
        self.primitive_dimensions_label.setMinimumWidth(100)
        self.status_bar_widget.addPermanentWidget(self.primitive_dimensions_label)

        # --- Signal connections ---
        self.menu_toolbar_widget.btn_settings.clicked.connect(self._on_settings_clicked)
        self.menu_toolbar_widget.btn_keyboard_shortcuts.clicked.connect(self._on_keyboard_shortcuts_clicked)
        self.menu_toolbar_widget.btn_help.clicked.connect(self._on_help_clicked)
        self.menu_toolbar_widget.btn_about.clicked.connect(self._on_about_clicked)

        # Plot toolbar connections
        self.draw_toolbar_widget.btn_plot_select_element.clicked.connect(self._on_select_tool_clicked)
        self.draw_toolbar_widget.btn_select_all.clicked.connect(self.select_all_items)
        self.draw_toolbar_widget.btn_move.clicked.connect(self._on_move_tool_clicked)
        self.draw_toolbar_widget.btn_rotate.clicked.connect(self._on_rotate_tool_clicked)
        self.draw_toolbar_widget.btn_scale.clicked.connect(self._on_scale_tool_clicked)

        # Setup Connection Points with selection menu using BasePopupMenuGrouped
        connection_types = [
            ("BW", _t("Butt Weld")),
            ("SW", _t("Socket Weld")),
            ("FL", _t("Flanged")),
            ("THD", _t("Threaded")),
            ("PL", _t("Plain")),
            ("CP", _t("Compression")),
            ("SC", _t("Screwed")),
            ("PE", _t("Plain End")),
            ("BE", _t("Beveled End")),
            ("TE", _t("Threaded End")),
        ]

        point_definitions = [
            (_t("Arrive Point"), "_on_draw_arrive_point_clicked"),
            (_t("Leave Point"), "_on_draw_leave_point_clicked"),
            (_t("Additional Point (Tee)"), "_on_draw_tee_point_clicked"),
        ]

        # Build connection groups dict
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
                lambda group_title, code: self._on_connection_popup_selected(code, action_by_group[group_title])
            )
        )

        # Setup Spindle Point with a selection menu using BasePopupMenuGrouped
        all_spindles = self.skey_service.get_all_spindles()
        self.properties_widget.update_spindles(all_spindles)

        # Build spindle groups dict from group_key/subgroup_key
        spindle_groups = {}
        for spindle in all_spindles:
            group = spindle.group_key
            subgroup = spindle.subgroup_key
            title = f"{group}/{subgroup}"
            spindle_groups.setdefault(title, {})[spindle.name] = f"spindles/{spindle.name}.svg"

        self.draw_toolbar_widget.btn_plot_point_spindle.setMenu(
            BasePopupMenuGrouped.create_menu(
                self.draw_toolbar_widget.btn_plot_point_spindle,
                _t("Select Spindle"),
                spindle_groups,
                self.icons_library_path,
                lambda _group, name: self._on_spindle_from_popup_selected(name)
            )
        )

        # Line tools menu - setup with grouped popup
        self.draw_toolbar_widget.setup_line_menu(self._on_line_tool_selected)

        # Shape tools menu - setup with grouped popup
        self.draw_toolbar_widget.setup_shapes_menu(self._on_shape_tool_selected)

        self.draw_toolbar_widget.btn_fill_color.setMenu(create_fill_color_menu(
            self.draw_toolbar_widget.btn_fill_color, self._on_fill_color_selected
        ))
        self.draw_toolbar_widget.btn_hatch.setMenu(create_hatch_menu(
            self.draw_toolbar_widget.btn_hatch, self._on_hatch_selected
        ))
        self.draw_toolbar_widget.btn_clear_sheet.clicked.connect(self.clear_canvas)

        # New menu toolbar connections
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
        """Update status bar with primitive coordinates and dimensions"""
        self.primitive_coords_label.setText(coords_str)
        self.primitive_dimensions_label.setText(dimensions_str)

    def _on_settings_clicked(self):
        """Opens the settings dialog and handles configuration changes."""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Handle language change
            lang_code = dialog.get_selected_language()
            if lang_code != get_current_language():
                self._change_language(lang_code)

            # Handle isometric view change
            iso_view = dialog.get_selected_isometric_view()
            self.preview_widget.set_isometric_view(iso_view)

            # Apply color changes
            self._apply_color_settings(dialog)

            # Refresh preview with new view
            if hasattr(self, 'current_skey_name') and self.current_skey_name:
                self.preview_widget.update_preview(
                    self.scene.symbol_drawlist,
                    self.origin_x,
                    self.origin_y
                )

    def _apply_color_settings(self, dialog):
        """Apply color settings from the dialog to the application."""
        from openiso.core import constants

        # Update point colors (also used in preview)
        point_colors = dialog.get_point_colors()
        for key, color in point_colors.items():
            constants.POINT_COLORS[key] = color

        # Update scene colors
        scene_colors = dialog.get_scene_colors()
        for key, color in scene_colors.items():
            constants.SCENE_COLORS[key] = color

        # Redraw the scene to apply new colors
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
        """Displays keyboard shortcuts dialog."""
        dialog = KeyboardShortcutsDialog(self)
        dialog.exec()

    def _on_about_clicked(self):
        """Displays information about the application."""
        dialog = AboutDialog(self.icons_library_path, self)
        dialog.exec()

    def _on_create_skey_requested(self):
        """Prepares the editor for creating a new Skey."""
        self.properties_widget.clear_fields()
        self.scene.clear_symbol_drawlist()
        self.preview_widget.update_preview([], self.origin_x, self.origin_y)
        self.status_bar_widget.showMessage(_t("Create new Skey"), 3000)

    def _on_delete_skey_requested(self, skey_name: str):
        """Deletes the specified Skey after confirmation."""
        # Find item to determine selection after delete
        current_item = self.tree_skeys.tree.currentItem()
        target_path = None

        if current_item and current_item.text(0) == skey_name:
            parent = current_item.parent()
            if parent and parent.parent():
                subgroup_name = parent.text(0)
                grandparent = parent.parent()
                group_name = grandparent.text(0) if grandparent else None

                # Skeys are at level 3 from treeRoot (Level 4 absolute)
                if grandparent and grandparent.parent():
                    index = parent.indexOfChild(current_item)
                    if parent.childCount() > 1:
                        # Select neighbor
                        neighbor_index = index + 1 if index < parent.childCount() - 1 else index - 1
                        neighbor_item = parent.child(neighbor_index)
                        if neighbor_item:
                            target_path = {
                                'group': group_name,
                                'subgroup': subgroup_name,
                                'skey': neighbor_item.text(0)
                            }
                    else:
                        # Subgroup will be empty
                        target_path = {
                            'group': group_name,
                            'subgroup': subgroup_name,
                            'skey': None
                        }

        reply = QMessageBox.question(
            self, _t("Delete Skey"),
            _t("Are you sure you want to delete Skey '{0}'?").format(skey_name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.skey_service.delete_skey(skey_name):
                self.refresh_skey_tree()

                # Re-select target item after refresh
                if target_path:
                    self.tree_skeys.select_item_by_path(
                        target_path['group'],
                        target_path['subgroup'],
                        target_path['skey']
                    )

                self.status_bar_widget.showMessage(_t("Skey '{0}' deleted").format(skey_name), 3000)
                # Clear properties if we deleted the currently edited Skey
                if self.properties_widget.txt_skey.text() == skey_name:
                    if not target_path or not target_path['skey']:
                        self._on_create_skey_requested()
            else:
                QMessageBox.critical(self, _t("Error"), _t("Failed to delete Skey '{0}'").format(skey_name))

    def _on_spindle_selected(self, spindle_skey_name):
        """Adds spindle geometry to the scene at the location of an existing SpindlePoint."""
        if not spindle_skey_name:
            return

        # Find SpindlePoint items in the scene
        spindle_points = []
        for item in self.scene.items():
            if isinstance(item, SpindlePoint):
                spindle_points.append(item)

        if not spindle_points:
            return

        # Fetch spindle geometry
        geometry_list = self.skey_service.get_spindle_geometry(spindle_skey_name)
        if not geometry_list:
            print(f"No geometry found for spindle: {spindle_skey_name}")
            return

        # For each spindle point found, add the spindle geometry centered at that point
        for point in spindle_points:
            pos = point.pos()
            # We assume point.pos() is already in scene pixels
            # We need to map relative spindle geometry to scene pixels centered at pos
            self._load_spindle_geometry_to_scene(geometry_list, pos.x(), pos.y())

    def _on_spindle_point_placed(self, spindle_name, pos):
        """Loads and positions spindle geometry onto the scene when a SpindlePoint is placed."""
        if not spindle_name:
            return

        print(f"Loading spindle geometry for '{spindle_name}' at {pos.x()}, {pos.y()}")
        geometry_list = self.skey_service.get_spindle_geometry(spindle_name)
        if not geometry_list:
            print(f"No geometry found for spindle: {spindle_name}")
            return

        self._load_spindle_geometry_to_scene(geometry_list, pos.x(), pos.y())
        self.preview_widget.update_preview(self.scene.symbol_drawlist, self.origin_x, self.origin_y)

    def _load_spindle_geometry_to_scene(self, geometry, base_x, base_y):
        """Loads and positions spindle geometry onto the scene based on a reference point."""
        # Simple point mapping for spindle elements
        # Note: Spindle geometry in DB might be relative or absolute.
        # Here we treat it as relative to 0,0 and offset it by base_x, base_y
        for item_str in geometry:
            try:
                item_type = item_str.split(":")[0].strip()
                if item_type in ("Line", "Rectangle", "Polygon", "Circle"):
                    # Process similar to _load_geometry_to_scene but with offset
                    parts = item_str.split(":")
                    if len(parts) < 2:
                        continue
                    params = parts[1].strip()
                    values = {}
                    for param in params.split():
                        if "=" in param:
                            key, val = param.split("=")
                            try:
                                values[key] = float(val)
                            except ValueError:
                                values[key] = val

                    if item_type == "Line":
                        x1 = values.get("x1", 0) * self.scene.step_x * 20 + base_x
                        y1 = base_y - values.get("y1", 0) * self.scene.step_y * 20
                        x2 = values.get("x2", 0) * self.scene.step_x * 20 + base_x
                        y2 = base_y - values.get("y2", 0) * self.scene.step_y * 20
                        line = QGraphicsLineItem(x1, y1, x2, y2)
                        line.setPen(QPen(QColor(0, 0, 0), 2))
                        self._add_graphics_element(line)
                    elif item_type == "Rectangle":
                        x0 = values.get("x0", 0) * self.scene.step_x * 20 + base_x
                        y0 = base_y - values.get("y0", 0) * self.scene.step_y * 20
                        w = values.get("width", 0) * self.scene.step_x * 20
                        h = values.get("height", 0) * self.scene.step_y * 20
                        rect = QGraphicsRectItem(x0 - w/2, y0 - h/2, w, h)
                        rect.setPen(QPen(QColor(0, 0, 0), 2))
                        self._add_graphics_element(rect)
                    elif item_type == "Polygon":
                        polygon = QPolygonF()
                        i = 1
                        while f"p{i}x" in values and f"p{i}y" in values:
                            px = values[f"p{i}x"] * self.scene.step_x * 20 + base_x
                            py = base_y - values[f"p{i}y"] * self.scene.step_y * 20
                            polygon.append(QPointF(px, py))
                            i += 1
                        if not polygon.isEmpty():
                            poly_item = QGraphicsPolygonItem(polygon)
                            poly_item.setPen(QPen(QColor(0, 0, 0), 2))
                            poly_item.setBrush(QBrush(QColor(150, 150, 150, 100)))
                            self._add_graphics_element(poly_item)
                    elif item_type == "Circle":
                        x0 = values.get("x0", 0) * self.scene.step_x * 20 + base_x
                        y0 = base_y - values.get("y0", 0) * self.scene.step_y * 20
                        r = values.get("r", 0) * self.scene.step_x * 20
                        circle = QGraphicsEllipseItem(x0 - r, y0 - r, 2 * r, 2 * r)
                        circle.setPen(QPen(QColor(0, 0, 0), 2))
                        self._add_graphics_element(circle)
            except Exception as e:
                print(f"Error drawing spindle item {item_str}: {e}")

    def _change_language(self, lang_code):
        """Switches the application's interface language and updates all translatable UI strings."""
        global _t, current_language_code
        _t = setup_i18n(lang_code)
        current_language_code = lang_code

        # Update all translatable UI texts without full UI rebuild
        self.setWindowTitle(_t("OpenIso - Skey Editor"))
        self.status_label.setText(_t("Ready"))
        self.group_skeys.setTitle(_t("Skeys List"))
        self.group_editor.setTitle(_t("Shape"))
        self.properties_widget.update_translations(_t)
        self.preview_widget.setTitle(_t("Preview"))
        self.menu_toolbar_widget.update_translations(_t)
        self.draw_toolbar_widget.update_translations(_t)
        self.tree_skeys.update_translations(_t)

        # Rebuild tree and reload data to update visible texts
        if self.skey_service.load_skeys():
            self.refresh_skey_tree()

    def _set_draw_action(self, action):
        """Sets the active drawing mode on the canvas and changes the mouse cursor to a crosshair."""
        QApplication.restoreOverrideCursor()
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.CrossCursor))
        self.scene.current_action = action
        # Reset movable flag for items when switching to a drawing tool
        for item in self.scene.symbol_drawlist:
            # Keep connection points movable as they might be handled differently,
            # but usually drawing tools should disable global moving.
            if not isinstance(item, PointItem):
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

    def _on_select_tool_clicked(self):
        """Activates the selection tool for interacting with existing elements on the canvas."""
        QApplication.restoreOverrideCursor()
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.scene.current_action = "select_element"
        self.scene.clearSelection()
        if hasattr(self.scene, 'selected_for_highlight'):
            for item in self.scene.selected_for_highlight:
                if hasattr(item, '_original_pen'):
                    item.setPen(item._original_pen)
                    del item._original_pen
                if hasattr(item, '_original_brush'):
                    item.setBrush(item._original_brush)
                    del item._original_brush
            self.scene.selected_for_highlight.clear()

        # Disable moving for primitives when in select mode
        for item in self.scene.symbol_drawlist:
            if not isinstance(item, PointItem):
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

    def _on_move_tool_clicked(self):
        """Activates the move tool to relocate elements on the canvas."""
        QApplication.restoreOverrideCursor()
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.SizeAllCursor))
        self.scene.current_action = "move_element"
        # Enable Movable flag for all items
        for item in self.scene.symbol_drawlist:
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

    def _on_rotate_tool_clicked(self):
        """Rotates selected elements on the canvas by 90 degrees."""
        self.rotate_element(90)

    def _on_scale_tool_clicked(self):
        """Opens a dialog to scale selected elements by a factor."""
        items = self.scene.selectedItems()
        if not items:
            self.status_bar_widget.showMessage(_t("No items selected to scale"), 3000)
            return

        scale, ok = QInputDialog.getDouble(self, _t("Scale Element"), _t("Scale Factor:"), 1.0, 0.01, 100.0, 2)
        if ok:
            self.scale_element(scale)

    def keyPressEvent(self, event):
        """Handles keyboard shortcuts and events."""
        # Get keyboard modifiers
        modifiers = event.modifiers()
        key = event.key()
        text = event.text()

        # File Operations
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            if text == 'i':  # Ctrl+I - Import File
                self.import_external_file()
                return
            elif text == 'e':  # Ctrl+E - Export File
                self.export_to_file()
                return
            elif text == 's':  # Ctrl+S - Save
                self.save_current_skey()
                return
            elif text == 'p':  # Ctrl+P - Print
                self.print_symbol()
                return
            elif text == 'z':  # Ctrl+Z - Undo
                self.undo_last_action()
                return
            elif text == 'y':  # Ctrl+Y - Redo
                self.redo_next_action()
                return
            elif text == 'a':  # Ctrl+A - Select All
                self.select_all_items()
                return
            elif text == ',':  # Ctrl+, - Settings
                self._on_settings_clicked()
                return
            elif text == 'h':  # Ctrl+H - About
                self._on_about_clicked()
                return
            elif key == Qt.Key.Key_Plus or text == '+':  # Ctrl++ - Zoom In
                self.zoom_in()
                return
            elif key == Qt.Key.Key_Minus or text == '-':  # Ctrl+- - Zoom Out
                self.zoom_out()
                return

        # Drawing Tools (single key shortcuts)
        elif modifiers == Qt.KeyboardModifier.NoModifier:
            if text.lower() == 'l':  # L - Line Tool
                self._on_draw_line_clicked()
                return
            elif text.lower() == 'p':  # P - Polyline Tool
                self._on_draw_polyline_clicked()
                return
            elif text.lower() == 'r':  # R - Rectangle Tool
                self._on_draw_rect_clicked()
                return
            elif text.lower() == 'c':  # C - Circle Tool
                self._on_draw_circle_clicked()
                return
            elif text.lower() == 'f':  # F - Fit to View
                self.fit_to_view()
                return
            elif key == Qt.Key.Key_Home:  # Home - Reset View
                self.reset_view()
                return
            elif key == Qt.Key.Key_Delete:  # Delete - Clear Sheet
                self.clear_canvas()
                return

        # Function Keys
        if key == Qt.Key.Key_F1:  # F1 - Help
            self._on_help_clicked()
            return

        # Escape key - Cancel current action
        if key == Qt.Key.Key_Escape:
            if hasattr(self.scene, 'selected_for_highlight'):
                for item in self.scene.selected_for_highlight:
                    if hasattr(item, '_original_pen'):
                        item.setPen(item._original_pen)
                        del item._original_pen
                    if hasattr(item, '_original_brush'):
                        item.setBrush(item._original_brush)
                        del item._original_brush
                self.scene.selected_for_highlight.clear()

            # Clear standard selection
            self.scene.clearSelection()

            QApplication.restoreOverrideCursor()
            self.scene.current_action = ""
            return

        QMainWindow.keyPressEvent(self, event)

    def _on_focus_item_changed(self, newItem, _oldItem, reason):
        """Slot to handle focus changes between items (currently a placeholder)."""
        if newItem and reason == Qt.FocusReason.MouseFocusReason:
            pass  # Item clicked

    def clear_canvas( self ):
        """Removes all user-drawn graphical elements from the current editing session."""
        for item in self.scene.symbol_drawlist:
            self.scene.removeItem( item )

    def select_all_items(self):
        """Select all items on the canvas."""
        self.scene.select_all_items()

    def _on_draw_arrive_point_clicked( self ):
        """Activates the tool to place an Arrive Point on the canvas."""
        self._set_draw_action("draw_arrive_point")

    def _on_draw_leave_point_clicked( self ):
        """Activates the tool to place a Leave Point on the canvas."""
        self._set_draw_action("draw_leave_point")

    def _on_draw_tee_point_clicked( self ):
        """Activates the tool to place a Tee Point on the canvas."""
        self._set_draw_action("draw_tee_point")

    def _on_draw_spindle_point_clicked( self ):
        """Activates the tool to place a Spindle (Valve) Point on the canvas."""
        self._set_draw_action("draw_spindle_point")

    def _on_draw_line_clicked( self ):
        """Activates the tool to draw a straight line on the canvas."""
        self._set_draw_action("draw_line")

    def _on_draw_polyline_clicked(self):
        """Activates the polyline tool."""
        self.status_bar_widget.showMessage(
            _t("Polyline: Click to add points, right-click or Enter to finish."),
            3000
        )
        self._set_draw_action("draw_polyline")

    def _on_draw_polyline_orthogonal_clicked(self):
        """Activates the orthogonal polyline tool."""
        self.status_bar_widget.showMessage(
            _t("Orthogonal Polyline: Click to add points, right-click or Enter to finish."),
            3000
        )
        self._set_draw_action("draw_polyline_orthogonal")

    def _parse_geometry_coordinate(self, item, index):
        """Extracts a numeric coordinate value from a formatted geometry parameter string."""
        return round(float(item.split(":")[1].split(" ")[index].split("=")[1]), 3) * 100.0

    def _add_graphics_element(self, element):
        """Helper method to add a new graphics item to the scene and the local tracking list."""
        element.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.scene.addItem(element)
        self.scene.symbol_drawlist.append(element)

    def _load_geometry_to_scene(self, geometry):
        """Parses geometry data strings and renders the corresponding items on the drawing canvas."""
        point_types = {
            "ArrivePoint": ArrivePoint,
            "LeavePoint": LeavePoint,
            "TeePoint": TeePoint,
            "SpindlePoint": SpindlePoint
        }

        for item_str in geometry:
            try:
                item_type = item_str.split(":")[0].strip()

                if item_type in point_types:
                    # Parse point: "ArrivePoint: x0=1.5 y0=2.3 type=BW"
                    parts = item_str.split(":")
                    if len(parts) < 2:
                        continue
                    params = parts[1].strip()
                    values = {}
                    for param in params.split():
                        if "=" in param:
                            key, val = param.split("=")
                            # Some values are floats (x0, y0), some are strings (name, type)
                            if key in ("x0", "y0"):
                                values[key] = float(val)
                            else:
                                values[key] = val

                    x0_rel = values.get("x0", 0)
                    y0_rel = values.get("y0", 0)
                    x0 = x0_rel * self.scene.step_x * 20 + self.scene.sheet_width / 2
                    y0 = self.scene.sheet_height / 2 - y0_rel * self.scene.step_y * 20

                    point_class = point_types[item_type]
                    if point_class == SpindlePoint:
                        spindle_name = values.get("name", "")
                        element = point_class(spindle_name=spindle_name,
                                              point_type=values.get("type", ""))
                        if spindle_name:
                            # Also load the graphics for this spindle at its position
                            geometry_list = self.skey_service.get_spindle_geometry(spindle_name)
                            if geometry_list:
                                self._load_spindle_geometry_to_scene(geometry_list, x0, y0)
                    else:
                        element = point_class(point_type=values.get("type", ""))

                    element.setPos(x0, y0)
                    self._add_graphics_element(element)

                elif item_type == "Line":
                    # Parse line: "Line: x1=1.5 y1=2.3 x2=3.5 y2=4.5"
                    parts = item_str.split(":")
                    if len(parts) < 2:
                        continue
                    params = parts[1].strip()
                    values = {}
                    for param in params.split():
                        if "=" in param:
                            key, val = param.split("=")
                            values[key] = float(val)

                    x1_rel = values.get("x1", 0)
                    y1_rel = values.get("y1", 0)
                    x2_rel = values.get("x2", 0)
                    y2_rel = values.get("y2", 0)
                    x1 = x1_rel * self.scene.step_x * 20 + self.scene.sheet_width / 2
                    y1 = self.scene.sheet_height / 2 - y1_rel * self.scene.step_y * 20
                    x2 = x2_rel * self.scene.step_x * 20 + self.scene.sheet_width / 2
                    y2 = self.scene.sheet_height / 2 - y2_rel * self.scene.step_y * 20
                    line = QGraphicsLineItem(x1, y1, x2, y2)
                    pen = QPen(QColor(0, 0, 0))
                    pen.setWidth(2)
                    line.setPen(pen)
                    self._add_graphics_element(line)

                elif item_type == "Rectangle":
                    # Parse rectangle: "Rectangle: x0=1.5 y0=2.3 width=3.0 height=4.0"
                    parts = item_str.split(":")
                    if len(parts) < 2:
                        continue
                    params = parts[1].strip()
                    values = {}
                    for param in params.split():
                        if "=" in param:
                            key, val = param.split("=")
                            values[key] = float(val)

                    x0_rel = values.get("x0", 0)
                    y0_rel = values.get("y0", 0)
                    width_rel = values.get("width", 0)
                    height_rel = values.get("height", 0)
                    x0 = x0_rel * self.scene.step_x * 20 + self.scene.sheet_width / 2
                    y0 = self.scene.sheet_height / 2 - y0_rel * self.scene.step_y * 20
                    width = width_rel * self.scene.step_x * 20
                    height = height_rel * self.scene.step_y * 20
                    rect = QGraphicsRectItem(x0 - width/2, y0 - height/2, width, height)
                    pen = QPen(QColor(0, 0, 0))
                    pen.setWidth(2)
                    rect.setPen(pen)
                    self._add_graphics_element(rect)

                elif item_type == "Polygon":
                    # Parse polygon: "Polygon: p1x=1.5 p1y=2.3 p2x=3.5 p2y=4.5 ..."
                    parts = item_str.split(":")
                    if len(parts) < 2:
                        continue
                    params = parts[1].strip()
                    values = {}
                    for param in params.split():
                        if "=" in param:
                            key, val = param.split("=")
                            values[key] = float(val)

                    polygon = QPolygonF()
                    i = 1
                    while f"p{i}x" in values and f"p{i}y" in values:
                        x = values[f"p{i}x"] * self.scene.step_x * 20 + self.scene.sheet_width / 2
                        y = self.scene.sheet_height / 2 - values[f"p{i}y"] * self.scene.step_y * 20
                        polygon.append(QPointF(x, y))
                        i += 1
                    if not polygon.isEmpty():
                        poly_item = QGraphicsPolygonItem(polygon)
                        pen = QPen(QColor(0, 0, 0))
                        pen.setWidth(2)
                        poly_item.setPen(pen)
                        poly_item.setBrush(QBrush(QColor(150, 150, 150, 100)))
                        self._add_graphics_element(poly_item)

                elif item_type == "Circle":
                    # Parse circle: "Circle: x0=1.5 y0=2.3 r=1.0"
                    parts = item_str.split(":")
                    if len(parts) < 2:
                        continue
                    params = parts[1].strip()
                    values = {}
                    for param in params.split():
                        if "=" in param:
                            key, val = param.split("=")
                            values[key] = float(val)

                    x0 = values.get("x0", 0) * self.scene.step_x * 20 + self.scene.sheet_width / 2
                    y0 = self.scene.sheet_height / 2 - values.get("y0", 0) * self.scene.step_y * 20
                    r = values.get("r", 0) * self.scene.step_x * 20
                    circle = QGraphicsEllipseItem(x0 - r, y0 - r, 2 * r, 2 * r)
                    pen = QPen(QColor(0, 0, 0))
                    pen.setWidth(2)
                    circle.setPen(pen)
                    self._add_graphics_element(circle)

            except Exception as e:
                print(f"Error loading geometry item '{item_str}': {e}")
                continue

        # Update preview after loading geometry
        self.preview_widget.update_preview(self.scene.symbol_drawlist, self.origin_x, self.origin_y)

    def _parse_raw_coordinate_pair(self, geometry: list, index: int) -> tuple:
        """Extracts X and Y floating-point coordinates from a raw geometry data array."""
        return float(geometry[index + 1]), float(geometry[index + 2])

    def _scale_and_offset_point(self, x: float, y: float, scale: float, symbol_width: float, symbol_height: float) -> tuple:
        """Scales relative coordinates to scene units and applies the necessary centering offsets."""
        scaled_x = round(x * scale - symbol_width / 2, 0) / 100.0
        scaled_y = round(y * scale - symbol_height / 2, 0) / 100.0
        return scaled_x, scaled_y

    def convert_raw_graphics_data(self, skey: str, geometry: list) -> list:
        """Converts legacy numeric graphics codes into the modern human-readable geometry string format."""
        self.scene.set_grid_center()

        # First pass: calculate bounds
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')

        for i in range(0, len(geometry), 3):
            code = geometry[i]
            if code in ("1", "2", "3", "6"):
                x, y = self._parse_raw_coordinate_pair(geometry, i)
                min_x, min_y = min(min_x, x), min(min_y, y)
                max_x, max_y = max(max_x, x), max(max_y, y)

        # Calculate scale - use a fixed scale or calculate without unit_size
        # Since we removed scale_factor and unit_size, we use a simple mapping
        # 0.05 is the old default (1/20 for 100px units)
        scale = 0.05

        symbol_width = max_x * scale
        symbol_height = max_y * scale

        # Find end index
        end_index = len(geometry)
        for i in range(0, len(geometry), 3):
            if geometry[i] == "0":
                end_index = i
                break

        # Second pass: generate geometry
        new_geometry = []
        start_x, start_y = 0.0, 0.0
        is_spindle = "SP" in skey

        for i in range(0, len(geometry), 3):
            code = geometry[i]

            if code == "1":  # Start/end point
                start_x, start_y = self._parse_raw_coordinate_pair(geometry, i)
                start_x, start_y = self._scale_and_offset_point(start_x, start_y, scale, symbol_width, symbol_height)

                if i == 0:
                    point_type = "SpindlePoint" if is_spindle else "ArrivePoint"
                    new_geometry.append(f"{point_type}: x0={start_x} y0={start_y}")
                elif i == len(geometry) - 3 or i == end_index - 3:
                    if not is_spindle:
                        new_geometry.append(f"LeavePoint: x0={start_x} y0={start_y}")

            elif code == "2":  # Line to
                end_x, end_y = self._parse_raw_coordinate_pair(geometry, i)
                end_x, end_y = self._scale_and_offset_point(end_x, end_y, scale, symbol_width, symbol_height)
                new_geometry.append(f"Line: x1={start_x} y1={start_y} x2={end_x} y2={end_y}")
                start_x, start_y = end_x, end_y

            elif code == "3":  # Tee point
                end_x, end_y = self._parse_raw_coordinate_pair(geometry, i)
                end_x, end_y = self._scale_and_offset_point(end_x, end_y, scale, symbol_width, symbol_height)
                new_geometry.append(f"TeePoint: x0={end_x} y0={end_y}")
                start_x, start_y = end_x, end_y

            elif code == "6":  # Spindle point
                end_x, end_y = self._parse_raw_coordinate_pair(geometry, i)
                end_x, end_y = self._scale_and_offset_point(end_x, end_y, scale, symbol_width, symbol_height)
                new_geometry.append(f"SpindlePoint: x0={end_x} y0={end_y}")
                start_x, start_y = end_x, end_y

        return new_geometry

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
        """Rebuilds the Skey tree view by fetching the latest group and symbol data from the service."""
        _t = setup_i18n()
        self.skey_service.reload_groups()

        # Update group combobox
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

        # Build tree using helper method
        self.tree_skeys.build_tree(groups, expanded=False)


    def import_external_file(self):
        """Placeholder for importing symbol data from a generic external file."""
        print("Import file clicked")

    def export_to_file(self):
        """Exports the current Skey data to an Intergraph ASCII (.asc) file."""
        skey_name = self.properties_widget.txt_skey.text().strip()
        if not skey_name:
            QMessageBox.warning(self, _t("Export Error"), _t("No Skey selected or name is empty"))
            return

        # Get current data (ensure it's updated from UI)
        group_key = self.properties_widget.cb_skey_group.currentData() or self.properties_widget.cb_skey_group.currentText()
        subgroup_key = self.properties_widget.cb_skey_subgroup.currentData() or self.properties_widget.cb_skey_subgroup.currentText()
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
            geometry=geometry
        )

        # Show Save Dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, _t("Export Skey as ASCII"),
            os.path.join(os.path.expanduser("~"), f"{skey_name}.asc"),
            _t("ASCII Symbolic File") + " (*.asc);;" + _t("All Files") + " (*)"
        )

        if not file_path:
            return

        try:
            ascii_content = self.skey_service.export_skey_to_ascii(skey)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(ascii_content)

            self.status_bar_widget.showMessage(_t("Skey '{0}' exported to {1}").format(skey_name, os.path.basename(file_path)), 3000)
            print(f"Skey '{skey_name}' exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, _t("Export Error"), _t("Failed to export Skey: {0}").format(str(e)))
            print(f"Export error: {e}")

    def print_symbol(self):
        """Opens the printing dialog to output the current symbol design."""
        print("Print clicked")

    def save_current_skey(self):
        """Gathers form data and scene geometry, and saves the Skey information to the database."""
        try:
            # Get current values from form
            skey_name = self.properties_widget.txt_skey.text().strip()
            group_key = self.properties_widget.cb_skey_group.currentData() or self.properties_widget.cb_skey_group.currentText()
            subgroup_key = self.properties_widget.cb_skey_subgroup.currentData() or self.properties_widget.cb_skey_subgroup.currentText()
            description_text = self.properties_widget.txt_skey_desc.toPlainText()
            spindle_skey = self.properties_widget.cb_spindle_skey.currentText()

            orientation = self.properties_widget.orientation_button_group.checkedId()
            flow_arrow = 2 if self.properties_widget.chk_flow_arrow.isChecked() else 1
            dimensioned = 2 if self.properties_widget.chk_dimensioned.isChecked() else 1
            tracing = 2 if self.properties_widget.chk_tracing.isChecked() else 1
            insulation = 2 if self.properties_widget.chk_insulation.isChecked() else 1

            # Collect geometry from scene
            geometry = self._collect_geometry_from_scene()

            if not skey_name:
                QMessageBox.warning(self, _t("Error"), _t("Skey name cannot be empty"))
                return False

            # Save to database
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
                lang_code=current_language_code
            )

            # Save changes
            self.skey_service.save_skeys()

            # Reload the tree and groups
            print(f"Reloading Skey tree after saving '{skey_name}'")
            self.refresh_skey_tree()

            # Reselect the saved skey in the tree
            self._select_skey_in_tree(skey_name)

            # Display the saved geometry
            self.properties_widget.display_geometry(geometry)

            self.status_bar_widget.showMessage(_t("Skey '{0}' saved successfully").format(skey_name), 3000)
            print(f"Skey '{skey_name}' saved successfully")
            return True

        except Exception as e:
            print(f"Error saving Skey: {e}")
            import traceback
            traceback.print_exc()
            return False

    def undo_last_action(self):
        """Reverts the last drawing or editing operation performed."""
        print("Undo clicked")

    def redo_next_action(self):
        """Re-applies the operation that was previously undone."""
        print("Redo clicked")

    def _select_skey_in_tree(self, skey_name: str):
        """Searches for and programmatically selects a specific Skey item in the tree view by its name."""
        root = self.tree_skeys.invisibleRootItem()
        if root is None:
            return

        def find_item(item, target_name):
            """Recursively search for item with target name."""
            # Compare with raw name stored in UserRole
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

    def _to_relative_coordinates(self, x: float, y: float) -> tuple:
        """Converts absolute scene pixel coordinates into relative symbolic coordinates used in the database."""
        rel_x = (x - self.scene.origin_x) / 100.0
        rel_y = -(y - self.scene.origin_y) / 100.0
        return rel_x, rel_y

    def _collect_geometry_from_scene(self):
        """Serializes all graphical elements on the canvas into a list of geometry data strings for saving."""
        geometry = []

        # Mapping of point types to their names
        point_types = {
            ArrivePoint: "ArrivePoint",
            LeavePoint: "LeavePoint",
            TeePoint: "TeePoint",
            SpindlePoint: "SpindlePoint"
        }

        for item in self.scene.symbol_drawlist:
            # Handle point types
            for point_class, name in point_types.items():
                if isinstance(item, point_class):
                    rel_x, rel_y = self._to_relative_coordinates(item.x(), item.y())
                    params = [f"x0={rel_x}", f"y0={rel_y}"]

                    if isinstance(item, SpindlePoint) and item.spindle_name:
                        params.append(f"name={item.spindle_name}")

                    if hasattr(item, 'point_type') and item.point_type:
                        params.append(f"type={item.point_type}")

                    geometry.append(f"{name}: {' '.join(params)}")
                    break
            else:
                # Handle other geometry types
                if isinstance(item, QGraphicsLineItem):
                    x1, y1 = self._to_relative_coordinates(item.line().p1().x(), item.line().p1().y())
                    x2, y2 = self._to_relative_coordinates(item.line().p2().x(), item.line().p2().y())
                    geometry.append(f"Line: x1={x1} y1={y1} x2={x2} y2={y2}")

                elif isinstance(item, QGraphicsRectItem):
                    pos = self.scene.convert_to_relative_position(QPointF(item.rect().x(), item.rect().y()))
                    width = round(item.rect().width() / self.scene.step_x / 20, 2)
                    height = round(item.rect().height() / self.scene.step_x / 20, 2)
                    geometry.append(f"Rectangle: x0={pos.x()} y0={pos.y()} width={width} height={height}")

                elif isinstance(item, QGraphicsPolygonItem):
                    parts = []
                    polygon = item.polygon()
                    for index in range(polygon.count()):
                        point = polygon.at(index)
                        pos = self.scene.convert_to_relative_position(point)
                        parts.append(f"x{index + 1}={pos.x()} y{index + 1}={pos.y()}")
                    geometry.append(f"Polygon: {' '.join(parts)}")

        return geometry

    def _show_file_open_dialog(self, extension: str) -> str | None:
        """Opens a native system file dialog to select a file with a specific extension."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, _t( "Select File" ),
            os.path.expanduser("~"),
            _t( "Symbols file" ) + f" (*.{extension})"
        )
        return file_path if file_path else None

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

    def import_from_idf_format( self ):
        """Executes the import process for Skey data from an Intergraph Data File (IDF)."""
        symbol_file_path = self._show_file_open_dialog( "idf" )
        if symbol_file_path is None:
            return

        result = self.skey_service.import_from_idf(symbol_file_path)
        if result.success:
            self.refresh_skey_tree()

    def move_element(self, axis, value):
        """Moves selected elements by a specific value along X or Y axis."""
        dx = value if axis == "X" else 0
        dy = -value if axis == "Y" else 0 # Y is inverted in Qt

        # Multiply by grid scale (10 pixels = 0.1 units)
        dx *= 100
        dy *= 100

        moved_count = 0
        for item in self.scene.selectedItems():
            item.moveBy(dx, dy)
            moved_count += 1

        if moved_count > 0:
            return f"Перемещено {moved_count} элементов на {value} по {axis}"
        return "Нет выделенных элементов для перемещения"

    def clear_selection(self):
        """Clears current selection on the canvas."""
        if hasattr(self.scene, 'selected_for_highlight'):
            for item in self.scene.selected_for_highlight:
                if hasattr(item, '_original_pen'):
                    item.setPen(item._original_pen)
                    del item._original_pen
                if hasattr(item, '_original_brush'):
                    item.setBrush(item._original_brush)
                    del item._original_brush
            self.scene.selected_for_highlight.clear()
        self.scene.clearSelection()
        return "Выделение снято"

    def rotate_element(self, angle):
        """Rotates selected elements on the canvas by a given angle."""
        try:
            angle = float(angle)
            items = self.scene.selectedItems()
            if not items:
                return "Нет выделенных элементов для поворота"

            for item in items:
                # Rotate around transform origin (default is 0,0 in item coords)
                item.setRotation(item.rotation() + angle)

            return f"Элементы ({len(items)}) повернуты на {angle} градусов"
        except ValueError:
            return "Ошибка: Некорректный угол поворота"

    def scale_element(self, factor):
        """Scales selected elements on the canvas by a given factor."""
        try:
            factor = float(factor)
            items = self.scene.selectedItems()
            if not items:
                return "Нет выделенных элементов для масштабирования"

            for item in items:
                item.setScale(item.scale() * factor)

            msg = f"Элементы ({len(items)}) масштабированы с коэффициентом {factor}"
            self.status_bar_widget.showMessage(msg, 3000)
            return msg
        except ValueError:
            return "Ошибка: Некорректный коэффициент масштабирования"

    def zoom_in(self):
        """Zooms in on the view by 20%."""
        self.view_editor.scale(1.2, 1.2)
        self.status_bar_widget.showMessage(_t("Zoomed in"), 1500)

    def zoom_out(self):
        """Zooms out on the view by 20%."""
        self.view_editor.scale(1/1.2, 1/1.2)
        self.status_bar_widget.showMessage(_t("Zoomed out"), 1500)

    def fit_to_view(self):
        """Fits the entire scene to the view."""
        self.view_editor.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.status_bar_widget.showMessage(_t("Fitted to view"), 1500)

    def reset_view(self):
        """Resets the view to the default zoom and position."""
        self.view_editor.resetTransform()
        self.view_editor.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.status_bar_widget.showMessage(_t("View reset"), 1500)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = SkeyEditor()
    main_window.show()
    sys.exit(app.exec())
