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
import logging

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSplitter,
    QSizePolicy,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from openiso import __app_id__, __version__
from openiso.core.app_context import AppContext
from openiso.core.constants import SHEET_SIZE
from openiso.core.i18n import setup_i18n
from openiso.core.parser import CommandParser
from openiso.core.user_settings import UserSettings
from openiso.core.workspace import ensure_workspace
from openiso.view.base_classes.base_popup_menu_grouped import BasePopupMenuGrouped
from openiso.view.graphics.scene import SheetLayout
from openiso.view.main_window.window_canvas import CanvasMixin
from openiso.view.main_window.window_controller import WindowController
from openiso.view.main_window.window_dialogs import DialogsMixin
from openiso.view.main_window.window_form_adapter import WindowFormAdapter, _checkbox_flag_value

# --- Mixin imports ---
from openiso.view.main_window.window_draw_tools import DrawToolsMixin
from openiso.view.main_window.window_fill_hatch import FillHatchMixin
from openiso.view.main_window.window_geometry_io import GeometryIOMixin
from openiso.view.main_window.window_skey_ops import SkeyOpsMixin
from openiso.view.popups.fill_color_popup import create_fill_color_menu
from openiso.view.popups.hatch_popup import create_hatch_menu
from openiso.view.widgets.draw_toolbar import DrawToolbarWidget
from openiso.view.widgets.menu_toolbar import MenuToolbarWidget
from openiso.view.widgets.preview import PreviewWidget
from openiso.view.widgets.properties import PropertiesWidget
from openiso.view.widgets.skey_tree import SkeyTreeView
from openiso.view.widgets.terminal import TerminalWidget

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)




# Initialize translations
_t = setup_i18n()
logger = logging.getLogger(__name__)


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

    _CHECKBOX_FLAG_MAP = {
        "user_definable": (1, 0),
        "flow_dependency": (1, 0),
        "isogen_standard": (1, 0),
    }

    def _set_save_button_dirty(self, dirty: bool):
        self._has_unsaved_changes = dirty
        if hasattr(self, "menu_toolbar_widget"):
            self.menu_toolbar_widget.set_save_dirty_state(dirty)

    def _mark_unsaved_changes(self):
        if getattr(self, "_suspend_dirty_tracking", False):
            return

        if self.current_skey_data is None and not getattr(self, "_is_creating_new_skey", False):
            return

        self._set_save_button_dirty(True)

    def _on_scene_symbol_changed(self):
        self._update_all_previews()
        self._mark_unsaved_changes()

    def _on_tree_skey_changed(self, current, _previous=None):
        """Handles the selection change in the Skey tree, loading the selected symbol's data."""
        if not current:
            return

        if current.childCount() > 0:
            return  # group / subgroup node, not a leaf

        skey_name = current.data(0, Qt.ItemDataRole.UserRole)
        if not skey_name:
            skey_name = current.text(0)

        logger.debug("Tree selection changed to: %s (raw: %s)", current.text(0), skey_name)

        skey_data = self.controller.get_skey(skey_name)
        if not skey_data:
            logger.error("Skey not found in repository: %s", skey_name)
            return

        self._suspend_dirty_tracking = True
        try:
            self.current_skey_data = skey_data
            self._is_creating_new_skey = False
            self.scene.clear_symbol_drawlist()
            self.properties_widget.load_skey_data(skey_data)

            if skey_data.geometry:
                logger.debug("Loading %d geometry items", len(skey_data.geometry))
                self._load_geometry_to_scene(skey_data.geometry)
            else:
                logger.debug("No geometry data found")

            self._update_all_previews()
        finally:
            self._suspend_dirty_tracking = False

        self._set_save_button_dirty(False)
        logger.debug("Skey %s loaded successfully", skey_name)

    def _on_group_changed(self, index):
        """Updates the subgroup selection list whenever the main Skey group is changed."""
        if index < 0:
            self._sync_current_skey_form_fields()
            return

        group_key = (
            self.properties_widget.cb_skey_group.currentData()
            or self.properties_widget.cb_skey_group.currentText()
        )
        if not group_key:
            self.properties_widget.cb_skey_subgroup.clear()
            self.properties_widget.cb_skey_subgroup.addItem("", "")
            self._sync_current_skey_form_fields()
            return

        self.properties_widget.cb_skey_subgroup.clear()
        subgroups = self.controller.get_subgroup_names(group_key)
        for subgroup in subgroups:
            self.properties_widget.cb_skey_subgroup.addItem(subgroup, subgroup)

        model = self.properties_widget.cb_skey_subgroup.model()
        if model:
            model.sort(0)

        self._sync_current_skey_form_fields()

    def _refresh_current_skey_json_preview(self):
        """Refresh JSON panel from current in-memory skey data."""
        skey_data = getattr(self, "current_skey_data", None)
        if skey_data is None:
            return

        self.properties_widget.display_geometry(getattr(skey_data, "geometry", []))

    def _sync_current_skey_form_fields(self):
        """Sync editable form fields to current SkeyData object."""
        skey_data = getattr(self, "current_skey_data", None)
        if skey_data is None:
            return

        props = self.properties_widget
        skey_data.group_key = props.cb_skey_group.currentData() or props.cb_skey_group.currentText() or ""
        skey_data.subgroup_key = (
            props.cb_skey_subgroup.currentData() or props.cb_skey_subgroup.currentText() or ""
        )
        skey_data.spindle_skey = props.cb_spindle_skey.currentText() or ""
        orientation = props.mirror_button_group.checkedId()
        if orientation >= 0:
            skey_data.orientation = orientation

        self._refresh_current_skey_json_preview()
        self._mark_unsaved_changes()

    def _on_subgroup_changed(self, _index):
        """Sync subgroup changes to current SkeyData."""
        self._sync_current_skey_form_fields()

    def _on_spindle_changed(self, _text):
        """Sync spindle changes to current SkeyData."""
        self._sync_current_skey_form_fields()

    def _on_orientation_changed(self, _id):
        """Sync orientation changes to current SkeyData."""
        self._sync_current_skey_form_fields()

    def _on_property_checkbox_toggled(self, field_name: str, state):
        """Keep current SkeyData flags synchronized with checkbox state."""
        skey_data = getattr(self, "current_skey_data", None)
        if skey_data is None:
            return

        if field_name in ("flow_arrow", "dimensioned", "tracing", "insulation"):
            setattr(skey_data, field_name, _checkbox_flag_value(state))
            self._refresh_current_skey_json_preview()
            self._mark_unsaved_changes()
            return

        mapping = self._CHECKBOX_FLAG_MAP.get(field_name)
        if mapping is None:
            return

        on_value, off_value = mapping
        setattr(skey_data, field_name, on_value if state else off_value)
        self._refresh_current_skey_json_preview()
        self._mark_unsaved_changes()

    def __init__(self, parent=None, application=None):
        """Initializes the SkeyEditor window, sets up data paths and business logic services."""
        QMainWindow.__init__(self, parent)
        self._application = application

        self.sheet_width = SHEET_SIZE
        self.sheet_height = SHEET_SIZE
        self.origin_x = self.sheet_width / 2
        self.origin_y = self.sheet_height / 2
        self.current_skey_data = None
        self._has_unsaved_changes = False
        self._suspend_dirty_tracking = False
        self._is_creating_new_skey = False

        if self._application is not None:
            context = self._application.context
        else:
            context = AppContext.build(__app_id__, __version__)
        self._context = context

        self.icons_library_path = str(context.paths.icons)
        logger.info("Initializing with data_path: %s", context.data_dir)

        self._load_styles(context.data_dir)

        if self._application is not None:
            self._settings = self._application.settings
        else:
            workspace = ensure_workspace()
            self._settings = UserSettings(json_path=workspace.settings_file)

        db_path_override = self._settings.get_str("database/path", "").strip()

        self.controller = WindowController(
            context,
            use_db=True,
            db_path=db_path_override or None,
        )
        # Keep backward-compatible access for existing mixins during incremental migration.
        self.skey_service = self.controller.skey_service
        self.help_window = None

        self._setup_ui()
        logger.debug("Calling load_skeys to populate tree...")
        if self.controller.load_initial_data(__version__):
            logger.debug("Successfully loaded skeys, populating tree...")
            self.refresh_skey_tree()
            self._handle_catalog_sync_feedback(self.controller.get_last_sync_result())
        else:
            logger.error("Failed to load skeys from database")

    def _setup_ui(self):
        """Sets up the user interface components, layouts and initial widget states."""
        cw = self.centralWidget()
        if cw is not None:
            self.setCentralWidget(None)

        # --- Widgets ---
        self.tree_skeys = SkeyTreeView(self.icons_library_path)
        self.group_skeys = QGroupBox()
        self.group_skeys.setMinimumWidth(180)
        self.vbox_lay_skeys = QVBoxLayout()
        self.group_skeys.setLayout(self.vbox_lay_skeys)

        self.group_editor = QGroupBox()
        self.vbox_lay_editor = QVBoxLayout()
        self.group_editor.setLayout(self.vbox_lay_editor)
        self.hbox_lay_editor = QHBoxLayout()
        self.vbox_lay_editor.addLayout(self.hbox_lay_editor)
        self.group_editor.setMinimumSize(self.sheet_width + 140, self.sheet_height + 100)
        self.group_editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.properties_widget = PropertiesWidget("", self.icons_library_path)
        self.form_adapter = WindowFormAdapter(self.properties_widget)
        self.menu_toolbar_widget = MenuToolbarWidget(self.icons_library_path)
        self.menu_toolbar_widget.set_save_dirty_state(False)
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
        self.scene.symbol_changed.connect(self._on_scene_symbol_changed)

        self._create_overlay_preview()

        self.hbox_lay_editor.addWidget(self.draw_toolbar_widget)
        self.hbox_lay_editor.addWidget(self.view_editor, stretch=1)

        if tuple(int(x) for x in __version__.split(".")) > (0, 9, 0):
            self.vbox_lay_editor.addWidget(self.terminal_widget)

        self.properties_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        self.form_properties_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.form_properties_splitter.setChildrenCollapsible(False)
        self.form_properties_splitter.addWidget(self.group_editor)
        self.form_properties_splitter.addWidget(self.properties_widget)
        self.form_properties_splitter.setStretchFactor(0, 1)
        self.form_properties_splitter.setStretchFactor(1, 0)
        self.form_properties_splitter.setSizes([self.sheet_width + 220, 360])

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.addWidget(self.group_skeys)
        self.main_splitter.addWidget(self.form_properties_splitter)
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setSizes([320, self.sheet_width + 220 + 360])

        self.hbox_lay_main = QHBoxLayout()
        self.hbox_lay_main.addWidget(self.main_splitter)

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

        self._update_all_previews()

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
        all_spindles = self.controller.get_all_spindles()
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

        self.tree_skeys.current_item_changed.connect(self._on_tree_skey_changed)
        self.tree_skeys.create_skey_requested.connect(self._on_create_skey_requested)
        self.tree_skeys.delete_skey_requested.connect(self._on_delete_skey_requested)
        self.properties_widget.cb_skey_group.currentIndexChanged.connect(self._on_group_changed)
        self.properties_widget.cb_skey_subgroup.currentIndexChanged.connect(self._on_subgroup_changed)
        self.properties_widget.cb_spindle_skey.currentTextChanged.connect(self._on_spindle_changed)
        self.properties_widget.cb_source_type.currentIndexChanged.connect(
            lambda _index: self._mark_unsaved_changes()
        )
        self.properties_widget.txt_skey.textChanged.connect(lambda _text: self._mark_unsaved_changes())
        self.properties_widget.txt_alias_code.textChanged.connect(lambda _text: self._mark_unsaved_changes())
        self.properties_widget.txt_skey_desc.textChanged.connect(self._mark_unsaved_changes)
        self.properties_widget.txt_source_name.textChanged.connect(lambda _text: self._mark_unsaved_changes())
        self.properties_widget.txt_source_version.textChanged.connect(lambda _text: self._mark_unsaved_changes())
        self.properties_widget.txt_pcf_identification.textChanged.connect(
            lambda _text: self._mark_unsaved_changes()
        )
        self.properties_widget.txt_idf_record.textChanged.connect(lambda _text: self._mark_unsaved_changes())
        self.properties_widget.mirror_button_group.idClicked.connect(self._on_orientation_changed)
        self.properties_widget.chk_flow_arrow.stateChanged.connect(
            lambda state: self._on_property_checkbox_toggled("flow_arrow", state)
        )
        self.properties_widget.chk_dimensioned.stateChanged.connect(
            lambda state: self._on_property_checkbox_toggled("dimensioned", state)
        )
        self.properties_widget.chk_tracing.stateChanged.connect(
            lambda state: self._on_property_checkbox_toggled("tracing", state)
        )
        self.properties_widget.chk_insulation.stateChanged.connect(
            lambda state: self._on_property_checkbox_toggled("insulation", state)
        )
        self.properties_widget.chk_user_definable.toggled.connect(
            lambda checked: self._on_property_checkbox_toggled("user_definable", checked)
        )
        self.properties_widget.chk_flow_dependency.toggled.connect(
            lambda checked: self._on_property_checkbox_toggled("flow_dependency", checked)
        )
        self.properties_widget.chk_isogen_standard.toggled.connect(
            lambda checked: self._on_property_checkbox_toggled("isogen_standard", checked)
        )
        self.scene.spindle_point_placed.connect(self._on_spindle_point_placed)
        self.scene.primitive_info_updated.connect(self._update_primitive_info_status)

    def _create_overlay_preview(self):
        """Create a lightweight preview overlay anchored to the top-right of the drawing area."""
        self.overlay_preview_widget = PreviewWidget(
            "",
            self.view_editor.viewport(),
            widget_size=(230, 160),
            scene_size=(190, 110),
        )
        self.overlay_preview_widget.setObjectName("OverlayPreview")
        self.overlay_preview_widget.setStyleSheet(self._build_overlay_preview_style(230))
        self._set_overlay_preview_opacity(0.7)
        self.overlay_preview_widget.setVisible(False)

        self.overlay_preview_widget.raise_()
        self._position_overlay_preview()

    def _build_overlay_preview_style(self, alpha: int):
        alpha = max(0, min(255, alpha))
        return (
            "QGroupBox#OverlayPreview {"
            f"background-color: rgba(255, 255, 255, {alpha});"
            "border: 1px solid rgba(60, 60, 60, 120);"
            "border-radius: 6px;"
            "margin-top: 0px;"
            "padding-top: 0px;"
            "}"
        )

    def set_overlay_preview_visible(self, visible: bool):
        """Show or hide the overlay preview panel."""
        overlay = getattr(self, "overlay_preview_widget", None)
        if overlay is None:
            return

        overlay.setVisible(visible)

    def _set_overlay_preview_visible(self, visible: bool):
        self.set_overlay_preview_visible(visible)

    def set_overlay_preview_opacity(self, opacity: float):
        """Set overlay preview opacity in the 0.0-1.0 range."""
        overlay = getattr(self, "overlay_preview_widget", None)
        if overlay is None:
            return

        alpha = int(round(max(0.0, min(1.0, opacity)) * 255))
        overlay.setStyleSheet(self._build_overlay_preview_style(alpha))

    def _set_overlay_preview_opacity(self, opacity: float):
        self.set_overlay_preview_opacity(opacity)

    def _position_overlay_preview(self):
        """Position overlay preview with a small margin from viewport edges."""
        overlay = getattr(self, "overlay_preview_widget", None)
        if overlay is None:
            return

        viewport = self.view_editor.viewport()
        margin = 8

        overlay_x = max(margin, viewport.width() - overlay.width() - margin)
        overlay_y = margin
        overlay.move(overlay_x, overlay_y)

    def _toggle_overlay_preview(self):
        """Toggle visibility of overlay preview panel in the drawing area."""
        overlay = getattr(self, "overlay_preview_widget", None)
        if overlay is None:
            return

        overlay.setVisible(not overlay.isVisible())
        if overlay.isVisible():
            self._position_overlay_preview()

    def _get_preview_widgets(self):
        """Return all preview widgets that must stay synchronized."""
        widgets = []
        overlay = getattr(self, "overlay_preview_widget", None)
        if overlay is not None:
            widgets.append(overlay)
        return widgets

    def _set_isometric_view_for_previews(self, iso_view):
        """Apply selected isometric orientation to all preview widgets."""
        for widget in self._get_preview_widgets():
            widget.set_isometric_view(iso_view)

    def _update_all_previews(self):
        """Keep all preview widgets synchronized with current scene geometry."""
        for widget in self._get_preview_widgets():
            widget.update_preview(self.scene.symbol_drawlist, self.origin_x, self.origin_y)

    def resizeEvent(self, event):
        """Reposition overlay preview whenever main window layout changes."""
        super().resizeEvent(event)
        self._position_overlay_preview()

    def eventFilter(self, watched, event):
        """Track viewport resizes so the overlay stays anchored to the top-right corner."""
        if watched is getattr(self.view_editor, "viewport", lambda: None)():
            if event.type() == QEvent.Type.Resize:
                self._position_overlay_preview()
            elif event.type() == QEvent.Type.Wheel and (
                event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                delta = event.angleDelta().y()
                if delta != 0:
                    factor = 1.12 if delta > 0 else (1 / 1.12)

                    current_scale = self.view_editor.transform().m11()
                    new_scale = current_scale * factor
                    if 0.05 <= new_scale <= 50.0:
                        old_anchor = self.view_editor.transformationAnchor()
                        self.view_editor.setTransformationAnchor(
                            QGraphicsView.ViewportAnchor.AnchorUnderMouse
                        )
                        self.view_editor.scale(factor, factor)
                        self.view_editor.setTransformationAnchor(old_anchor)

                event.accept()
                return True
        return super().eventFilter(watched, event)

    def showEvent(self, event):
        """Position the overlay after the main window becomes visible."""
        super().showEvent(event)
        self._position_overlay_preview()

    def _update_primitive_info_status(self, coords_str, dimensions_str):
        """Update status bar with primitive coordinates and dimensions."""
        self.primitive_coords_label.setText(coords_str)
        self.primitive_dimensions_label.setText(dimensions_str)

    def _change_language(self, lang_code):
        """Switches the application's interface language and updates all translatable UI strings."""
        translator = setup_i18n(lang_code)
        globals()["_t"] = translator

        self.setWindowTitle(translator("OpenIso - Iso Symbols Library Editor"))
        self.status_label.setText(translator("Ready"))
        self.group_skeys.setTitle("")
        self.group_editor.setTitle("")
        self.properties_widget.update_translations(translator)
        if hasattr(self, "overlay_preview_widget"):
            self.overlay_preview_widget.setTitle("")
        self.menu_toolbar_widget.update_translations(translator)
        self.draw_toolbar_widget.update_translations(translator)
        self.tree_skeys.update_translations(translator)

        if self.controller.load_skeys():
            self.refresh_skey_tree()

    def _load_styles(self, data_path):
        """Loads global CSS styles from the data directory."""
        style_path = os.path.join(data_path, "style.css")
        if os.path.exists(style_path):
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
            except (OSError, UnicodeError) as err:
                logger.warning("Error loading CSS: %s", err)

    def refresh_skey_tree(self):
        """Rebuilds the Skey tree view from the latest service data."""
        _t = setup_i18n()
        self.controller.reload_groups()

        self.properties_widget.cb_skey_group.clear()
        self.properties_widget.cb_skey_group.addItem("", "")
        groups = self.controller.get_groups()
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
