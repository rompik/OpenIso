# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import os

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout

from openiso.core.i18n import setup_i18n

_t = setup_i18n()

class BaseMenuPopupItem(QPushButton):
    item_selected = pyqtSignal(str, str) # Emits (category, item_name)

    def __init__(self, category, name, icon_path, size=48, item_width=None, parent=None):
        super().__init__(parent)
        self.category = category
        self.item_name = name
        self.item_value = name
        # Keep enough room for translated labels to wrap instead of clipping.
        width = item_width if item_width is not None else (size + 28)
        self.setFixedSize(width, size + 52)
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
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.name_label.setWordWrap(True)
        self.name_label.setMinimumHeight(36)
        self.name_label.setMaximumWidth(max(10, width - 8))
        self.name_label.setToolTip(name)
        self.name_label.setProperty("class", "BasePopupItemName")

        layout.addWidget(self.icon_label)
        layout.addWidget(self.name_label)
        self.clicked.connect(lambda: self.item_selected.emit(self.category, self.item_value))
