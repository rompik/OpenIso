# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import os
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QLabel
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from openiso.core.i18n import setup_i18n

_t = setup_i18n()

class BaseMenuPopupItem(QPushButton):
    item_selected = pyqtSignal(str, str) # Emits (category, item_name)

    def __init__(self, category, name, icon_path, size=48, parent=None):
        super().__init__(parent)
        self.category = category
        self.item_name = name
        self.setFixedSize(size + 10, size + 25)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("class", "BaseMenuPopupItem")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        self.icon_label = QLabel()
        self.icon_label.setProperty("class", "BaseMenuPopupItemIcon")

        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            icon_size = QSize(size, size)
            pixmap = icon.pixmap(icon_size).scaled(size, size,
                                                   Qt.AspectRatioMode.KeepAspectRatio,
                                                   Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)
        else:
            self.icon_label.setText("❓")

        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setProperty("class", "BasePopupItemName")

        layout.addWidget(self.icon_label)
        layout.addWidget(self.name_label)
        self.clicked.connect(lambda: self.item_selected.emit(self.category, self.item_name))