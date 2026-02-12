# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout,
    QPushButton, QLabel, QMenu, QWidgetAction, QFrame, QScrollArea
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from openiso.core.i18n import setup_i18n

_t = setup_i18n()

# Common ISOGEN connection codes
CONNECTION_TYPES = [
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

class ConnectionItem(QPushButton):
    connection_selected = pyqtSignal(str)

    def __init__(self, name, description="", size=48, icons_path=None, parent=None):
        super().__init__(parent)
        self.connection_name = name
        self.setFixedSize(size + 10, size + 25)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"{name}: {description}" if description else name)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # Icon
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if icons_path:
            icon_file = os.path.join(icons_path, "connections", f"{name.lower()}.svg")
            if os.path.exists(icon_file):
                self.icon_label.setPixmap(QPixmap(icon_file).scaled(
                    size, size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
            else:
                self.icon_label.setText("❓")
                self.icon_label.setProperty("class", "ConnectionItemIcon")

        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setProperty("class", "ConnectionItemName")

        layout.addWidget(self.icon_label)
        layout.addWidget(self.name_label)

        self.clicked.connect(lambda: self.connection_selected.emit(self.connection_name))
        self.setProperty("class", "ConnectionItem")

class ConnectionPopup(QWidget):
    # Emits (connection_type, action_name)
    connection_selected = pyqtSignal(str, str)

    def __init__(self, title=_t("Select Connection Point Type"), icons_path=None, parent=None):
        super().__init__(parent)
        self.setFixedWidth(380)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Title
        self.lbl_title = QLabel(title)
        self.lbl_title.setProperty("class", "ConnectionPopupTitle")
        self.main_layout.addWidget(self.lbl_title)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setMaximumHeight(600)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(15)
        self.scroll_layout.setContentsMargins(0, 0, 5, 0)

        # Define points to display
        points = [
            (_t("Arrive Point"), "_on_draw_arrive_point_clicked"),
            (_t("Leave Point"), "_on_draw_leave_point_clicked"),
            (_t("Additional Point (Tee)"), "_on_draw_tee_point_clicked"),
        ]

        for point_title, action in points:
            group_box = QFrame()
            group_box.setProperty("class", "ConnectionGroupBox")
            group_layout = QVBoxLayout(group_box)

            group_label = QLabel(point_title)
            group_label.setProperty("class", "ConnectionGroupLabel")
            group_layout.addWidget(group_label)

            grid = QGridLayout()
            grid.setSpacing(8)
            cols = 5
            for i, (name, description) in enumerate(CONNECTION_TYPES):
                r, c = divmod(i, cols)
                item = ConnectionItem(name, description, size=40, icons_path=icons_path)

                # Use a specific slot method logic with captured action to avoid lambda issues
                def make_emit_handler(current_action):
                    return lambda c_type: self.connection_selected.emit(c_type, current_action)

                item.connection_selected.connect(make_emit_handler(action))
                grid.addWidget(item, r, c)

            group_layout.addLayout(grid)
            self.scroll_layout.addWidget(group_box)

        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

def create_connection_menu(parent_button, title, callback, icons_path=None):
    """Utility to create a QMenu with the ConnectionPopup encapsulated."""
    menu = QMenu(parent_button)
    popup = ConnectionPopup(title=title, icons_path=icons_path)

    action = QWidgetAction(menu)
    action.setDefaultWidget(popup)
    menu.addAction(action)

    # Bridge signals: popup.connection_selected(conn_type, action_name)
    popup.connection_selected.connect(lambda conn_type, action_name: menu.close())
    popup.connection_selected.connect(callback)

    return menu
