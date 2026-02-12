# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame, QMenu
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QAction
from openiso.core.constants import BUTTON_SIZE, ICONS
from openiso.core.i18n import setup_i18n

_t = setup_i18n()

class DrawToolbarWidget(QWidget):
    """
    Component for the drawing tool buttons panel.
    """
    def __init__(self, icons_path, parent=None):
        super().__init__(parent)
        self.icons_library_path = icons_path
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        self.setup_ui()

    def _create_tool_button(self, tooltip, icon_path, size=BUTTON_SIZE, has_menu=False):
        btn = QPushButton()
        btn.setToolTip(_t(tooltip))
        icon_full_path = os.path.join(self.icons_library_path, icon_path)
        if os.path.exists(icon_full_path):
            btn.setIcon(QIcon(icon_full_path))
        btn.setIconSize(QSize(size, size))
        btn.setFixedSize(size, size)
        # Use CSS class from style.css
        if has_menu:
            btn.setProperty("class", "ToolButtonWithMenu")
        else:
            btn.setProperty("class", "ToolButton")
        return btn

    def _add_separator(self):
        """Adds a horizontal line separator to the vertical layout."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setProperty("class", "ToolbarSeparator")
        self.layout.addWidget(line)

    def setup_ui(self):
        # 1. Edit / History Group
        self.btn_plot_select_element = self._create_tool_button("Select Element", ICONS["select_element"])
        self.btn_select_all = self._create_tool_button("Select All", ICONS["select_all"])
        self.btn_move = self._create_tool_button("Move", ICONS["move"])
        self.btn_rotate = self._create_tool_button("Rotate", ICONS["rotate"])
        self.btn_scale = self._create_tool_button("Scale", ICONS["scale"])
        self.btn_undo = self._create_tool_button("Undo", ICONS["undo"])
        self.btn_redo = self._create_tool_button("Redo", ICONS["redo"])

        # 2. Connection Points Group
        self.btn_plot_connections = self._create_tool_button("Draw Connection Point", ICONS["point_arrive"])
        self.btn_plot_point_spindle = self._create_tool_button("Draw Spindle Connection Point", ICONS["point_spindle"])

        # 3. Shapes Group
        # Line Tools Button with Menu
        self.btn_plot_line = self._create_tool_button("Draw Line", ICONS["line"], has_menu=True)
        self.line_menu = QMenu()

        # Create line tool actions
        self.action_line = QAction(QIcon(os.path.join(self.icons_library_path, ICONS["line"])), _t("Line"), self)
        self.action_polyline = QAction(QIcon(os.path.join(self.icons_library_path, ICONS["polyline"])), _t("Polyline"), self)
        self.action_polyline_orthogonal = QAction(QIcon(os.path.join(self.icons_library_path, ICONS["polyline_orthogonal"])), _t("Orthogonal Polyline"), self)

        self.line_menu.addAction(self.action_line)
        self.line_menu.addAction(self.action_polyline)
        self.line_menu.addAction(self.action_polyline_orthogonal)

        self.btn_plot_line.setMenu(self.line_menu)

        # Basic Shapes Button with Menu
        self.btn_plot_shapes = self._create_tool_button("Draw Shape", ICONS["square"], has_menu=True)
        self.shapes_menu = QMenu()

        # Create shape tool actions
        self.action_square = QAction(QIcon(os.path.join(self.icons_library_path, ICONS["square"])), _t("Square"), self)
        self.action_rectangle = QAction(QIcon(os.path.join(self.icons_library_path, ICONS["rectangle"])), _t("Rectangle"), self)
        self.action_circle = QAction(QIcon(os.path.join(self.icons_library_path, ICONS["circle"])), _t("Circle"), self)
        self.action_triangle = QAction(QIcon(os.path.join(self.icons_library_path, ICONS["triangle"])), _t("Triangle"), self)

        self.shapes_menu.addAction(self.action_square)
        self.shapes_menu.addAction(self.action_rectangle)
        self.shapes_menu.addAction(self.action_circle)
        self.shapes_menu.addAction(self.action_triangle)

        self.btn_plot_shapes.setMenu(self.shapes_menu)

        self.btn_plot_diamond = self._create_tool_button("Draw Diamond", ICONS["diamond"])
        self.btn_plot_cap = self._create_tool_button("Draw Dish", ICONS["cap"])
        self.btn_plot_hexagon = self._create_tool_button("Draw Hexagon", ICONS["hexagon"])

        # 4. Styling Group
        self.btn_fill_color = self._create_tool_button("Fill Color", ICONS["fill_colors"])

        # Special
        self.btn_clear_sheet = self._create_tool_button("Clear Sheet", ICONS["clear_sheet"])


        # Add to layout with groups and separators
        edit_group = [
            self.btn_plot_select_element, self.btn_select_all, self.btn_move,
            self.btn_rotate, self.btn_scale, self.btn_undo, self.btn_redo
        ]
        for btn in edit_group:
            self.layout.addWidget(btn)

        self._add_separator()

        conn_group = [self.btn_plot_connections, self.btn_plot_point_spindle]
        for btn in conn_group:
            self.layout.addWidget(btn)

        self._add_separator()

        shape_group = [
            self.btn_plot_line,
            self.btn_plot_shapes,
            self.btn_plot_diamond, self.btn_plot_cap, self.btn_plot_hexagon
        ]
        for btn in shape_group:
            self.layout.addWidget(btn)

        self._add_separator()
        self.layout.addWidget(self.btn_fill_color)
        self.layout.addStretch()
        self.layout.addWidget(self.btn_clear_sheet)

    def update_translations(self, _t):
        self.btn_plot_select_element.setToolTip(_t("Select Element"))
        self.btn_select_all.setToolTip(_t("Select All"))
        self.btn_move.setToolTip(_t("Move"))
        self.btn_rotate.setToolTip(_t("Rotate"))
        self.btn_scale.setToolTip(_t("Scale"))
        self.btn_undo.setToolTip(_t("Undo"))
        self.btn_redo.setToolTip(_t("Redo"))
        self.btn_plot_connections.setToolTip(_t("Draw Connection Point"))
        self.btn_plot_point_spindle.setToolTip(_t("Draw Spindle Connection Point"))
        self.btn_plot_line.setToolTip(_t("Draw Line"))
        self.action_line.setText(_t("Line"))
        self.action_polyline.setText(_t("Polyline"))
        self.action_polyline_orthogonal.setText(_t("Orthogonal Polyline"))
        self.btn_plot_shapes.setToolTip(_t("Draw Shape"))
        self.action_square.setText(_t("Square"))
        self.action_rectangle.setText(_t("Rectangle"))
        self.action_circle.setText(_t("Circle"))
        self.action_triangle.setText(_t("Triangle"))
        self.btn_plot_diamond.setToolTip(_t("Draw Diamond"))
        self.btn_plot_cap.setToolTip(_t("Draw Dish"))
        self.btn_plot_hexagon.setToolTip(_t("Draw Hexagon"))
        self.btn_fill_color.setToolTip(_t("Fill Color"))
        self.btn_clear_sheet.setToolTip(_t("Clear Sheet"))
