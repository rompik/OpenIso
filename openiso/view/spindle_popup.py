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

class SpindleItem(QPushButton):
    spindle_selected = pyqtSignal(str)

    def __init__(self, name, icon_path, description="", size=48, parent=None):
        super().__init__(parent)
        self.spindle_name = name
        self.setFixedSize(size + 10, size + 25)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"{name}: {description}" if description else name)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        self.icon_label = QLabel()
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setProperty("class", "SpindleItemName")

        layout.addWidget(self.icon_label)
        layout.addWidget(self.name_label)

        self.clicked.connect(lambda: self.spindle_selected.emit(self.spindle_name))
        self.setProperty("class", "SpindleItem")

class SpindlePopup(QWidget):
    spindle_selected = pyqtSignal(str)

    def __init__(self, spindles, icons_path, parent=None):
        super().__init__(parent)
        self.setFixedWidth(350)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)

        # Label
        self.lbl_title = QLabel(_t("Select Spindle"))
        self.lbl_title.setProperty("class", "SpindlePopupTitle")
        self.layout.addWidget(self.lbl_title)

        # Scroll Area for spindles
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setMaximumHeight(400)

        self.scroll_widget = QWidget()
        self.grid = QGridLayout(self.scroll_widget)
        self.grid.setSpacing(5)
        self.grid.setContentsMargins(5, 5, 5, 5)

        if not spindles:
            no_data = QLabel(_t("No spindles found in database"))
            no_data.setProperty("class", "SpindleNoData")
            no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid.addWidget(no_data, 0, 0)
        else:
            cols = 4
            for i, spindle in enumerate(spindles):
                # Handle both SkeyData objects and legacy (name, description) tuples
                if hasattr(spindle, 'name'):
                    name = spindle.name
                    # Try to get description from i18n
                    description = _t(spindle.description_key) if spindle.description_key else ""
                else:
                    name = spindle[0]
                    description = spindle[1] if len(spindle) > 1 else ""

                r, c = divmod(i, cols)
                # Try to find icon: NAME.svg
                icon_file = f"{name}.svg"
                icon_path = os.path.join(icons_path, "spindles", icon_file)

                item = SpindleItem(name, icon_path, description)
                item.spindle_selected.connect(self.spindle_selected)
                self.grid.addWidget(item, r, c)

            self.grid.setRowStretch(len(spindles) // cols + 1, 1)

        self.scroll.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll)

def create_spindle_menu(parent_button, spindles, icons_path, callback):
    menu = QMenu(parent_button)
    popup = SpindlePopup(spindles, icons_path)

    action = QWidgetAction(menu)
    action.setDefaultWidget(popup)
    menu.addAction(action)

    def on_spindle_selected(name):
        callback(name)
        menu.close()

    popup.spindle_selected.connect(on_spindle_selected)
    return menu
