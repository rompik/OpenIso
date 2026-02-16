# SPDX-License-Identifier: MIT
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
    """Individual connection type button item."""
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
    """Popup for selecting connection type with grouped point types.

    This popup organizes connection types into groups by point type
    (Arrive, Leave, Tee) and emits the selected connection type along
    with the action name associated with that point type.

    Signal: connection_selected(connection_type: str, action_name: str)
    """
    # Emits (connection_type, action_name)
    connection_selected = pyqtSignal(str, str)

    # Define point types and their associated actions
    POINT_DEFINITIONS = [
        (_t("Arrive Point"), "_on_draw_arrive_point_clicked"),
        (_t("Leave Point"), "_on_draw_leave_point_clicked"),
        (_t("Additional Point (Tee)"), "_on_draw_tee_point_clicked"),
    ]

    def __init__(self, title=_t("Select Connection Point Type"), icons_path=None, parent=None):
        super().__init__(parent)
        self.icons_path = icons_path
        self.setFixedWidth(380)

        self._setup_ui(title)

    def _setup_ui(self, title):
        """Initialize the user interface with title and scrollable sections."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Title
        lbl_title = QLabel(title)
        lbl_title.setProperty("class", "ConnectionPopupTitle")
        self.main_layout.addWidget(lbl_title)

        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setMaximumHeight(600)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(0, 0, 5, 0)

        # Add point type sections
        for point_title, action in self.POINT_DEFINITIONS:
            section = self._create_point_section(point_title, action)
            scroll_layout.addWidget(section)

        scroll_area.setWidget(scroll_content)
        self.main_layout.addWidget(scroll_area)

    def _create_point_section(self, point_title, action):
        """Create a section frame for a point type with connection items."""
        group_box = QFrame()
        group_box.setProperty("class", "ConnectionGroupBox")
        group_layout = QVBoxLayout(group_box)

        # Section title
        group_label = QLabel(point_title)
        group_label.setProperty("class", "ConnectionGroupLabel")
        group_layout.addWidget(group_label)

        # Grid of connection items
        grid = QGridLayout()
        grid.setSpacing(8)
        cols = 5

        for i, (name, description) in enumerate(CONNECTION_TYPES):
            row, col = divmod(i, cols)
            item = ConnectionItem(name, description, size=40, icons_path=self.icons_path)

            # Connect signal with action captured in closure
            item.connection_selected.connect(
                lambda conn_type, current_action=action: self.connection_selected.emit(conn_type, current_action)
            )
            grid.addWidget(item, row, col)

        group_layout.addLayout(grid)
        return group_box


def create_connection_menu(parent_button, title, callback, icons_path=None):
    """Create a QMenu with the ConnectionPopup encapsulated.

    Args:
        parent_button: The parent widget that owns the menu
        title: Title text for the popup
        callback: Function to call when connection is selected, signature: callback(conn_type, action_name)
        icons_path: Path to the icons directory

    Returns:
        QMenu: A menu widget containing the connection popup
    """
    menu = QMenu(parent_button)
    popup = ConnectionPopup(title=title, icons_path=icons_path)

    action = QWidgetAction(menu)
    action.setDefaultWidget(popup)
    menu.addAction(action)

    # Bridge signals: popup.connection_selected(conn_type, action_name)
    popup.connection_selected.connect(lambda conn_type, action_name: menu.close())
    popup.connection_selected.connect(callback)

    return menu
