# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame, QMenu
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QAction
from openiso.core.constants import BUTTON_SIZE, ICONS
from openiso.core.i18n import setup_i18n
from openiso.view.base_classes.base_popup_menu_grouped import BasePopupMenuGrouped

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
        # Line Tools Button with Grouped Menu
        self.btn_plot_line = self._create_tool_button("Draw Lines", ICONS["menu_line"], has_menu=True)
        self.btn_plot_line.setObjectName("LineToolButton")

        # Define line tools grouped structure
        self.line_groups = {
            _t("Lines"): {
                _t("Line"): ICONS["line"],
                _t("Polyline"): ICONS["polyline"],
                _t("Orthogonal Polyline"): ICONS["polyline_orthogonal"]
            }
        }

        # Basic Shapes Button with Grouped Menu
        self.btn_plot_shapes = self._create_tool_button("Draw Primitive", ICONS["menu_primitive"], has_menu=True)
        self.btn_plot_shapes.setObjectName("ShapesToolButton")

        # Define shape tools grouped structure
        self.shapes_groups = {
            _t("Basic Shapes"): {
                _t("Square"): ICONS["square"],
                _t("Rectangle"): ICONS["rectangle"],
                _t("Circle"): ICONS["circle"],
                _t("Triangle"): ICONS["triangle"]
            },
            _t("Special Shapes"): {
                _t("Cap"): ICONS["cap"],
                _t("Diamond"): ICONS["diamond"],
                _t("Pentagon"): ICONS["pentagon"],
                _t("Hexagon"): ICONS["hexagon"],
                _t("Octagon"): ICONS["octagon"],
                _t("Dodecagon"): ICONS["dodecagon"]
            }
        }

        self.btn_fill_color = self._create_tool_button("Fill Color", ICONS["fill_colors"])
        self.btn_hatch = self._create_tool_button("Hatch Pattern", ICONS["hatch"])
        self.btn_clear_sheet = self._create_tool_button("Clear Sheet", ICONS["clear_sheet"])


        # Add to layout with groups and separators
        conn_group = [self.btn_plot_connections, self.btn_plot_point_spindle]
        for btn in conn_group:
            self.layout.addWidget(btn)

        self._add_separator()

        shape_group = [
            self.btn_plot_line,
            self.btn_plot_shapes
        ]

        for btn in shape_group:
            self.layout.addWidget(btn)

        self._add_separator()
        self.layout.addWidget(self.btn_fill_color)
        self.layout.addWidget(self.btn_hatch)
        self.layout.addStretch()
        self.layout.addWidget(self.btn_clear_sheet)

    def setup_line_menu(self, callback):
        """Setup the line tools menu with grouped popup.

        Args:
            callback: Function to call when line tool is selected,
                     signature: callback(category, tool_name)
        """
        self.btn_plot_line.setMenu(
            BasePopupMenuGrouped.create_menu(
                self.btn_plot_line,
                _t("Select Line Tool"),
                self.line_groups,
                self.icons_library_path,
                callback
            )
        )

    def setup_shapes_menu(self, callback):
        """Setup the shape tools menu with grouped popup.

        Args:
            callback: Function to call when shape tool is selected,
                     signature: callback(category, tool_name)
        """
        self.btn_plot_shapes.setMenu(
            BasePopupMenuGrouped.create_menu(
                self.btn_plot_shapes,
                _t("Select Primitive Tool"),
                self.shapes_groups,
                self.icons_library_path,
                callback
            )
        )

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
        self.btn_plot_line.setToolTip(_t("Draw Lines"))
        self.btn_plot_shapes.setToolTip(_t("Draw Primitive"))
        self.btn_fill_color.setToolTip(_t("Fill Color"))
        self.btn_hatch.setToolTip(_t("Hatch Pattern"))
        self.btn_clear_sheet.setToolTip(_t("Clear Sheet"))
