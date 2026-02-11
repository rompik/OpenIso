# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QComboBox, QMenu, QWidgetAction, QColorDialog,
    QFrame
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, pyqtSignal
from openiso.core.i18n import setup_i18n
from openiso.core.constants import FILL_COLORS_PALETTE, RECENT_FILL_COLORS

_t = setup_i18n()

class ColorSwatch(QPushButton):
    colorSelected = pyqtSignal(QColor)

    def __init__(self, color, size=24, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(lambda: self.colorSelected.emit(self.color))
        self.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc; border-radius: 2px;")

class FillColorPopup(QWidget):
    colorSelected = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)

        # Label
        self.lbl_title = QLabel(_t("Fill Color"))
        self.lbl_title.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.lbl_title)

        # Category/Theme Combo (Mockup)
        self.cb_theme = QComboBox()
        self.cb_theme.addItem("material")
        self.layout.addWidget(self.cb_theme)

        # Color Grid
        self.grid = QGridLayout()
        self.grid.setSpacing(2)

        # Sample colors (Material Palette)
        colors = FILL_COLORS_PALETTE

        cols = 9
        for i, color_hex in enumerate(colors):
            r, c = divmod(i, cols)
            swatch = ColorSwatch(QColor(color_hex))
            swatch.colorSelected.connect(self.colorSelected)
            self.grid.addWidget(swatch, r, c)

        self.layout.addLayout(self.grid)

        # Recent colors (Placeholder)
        self.layout.addWidget(QLabel(_t("Recent")))
        self.recent_layout = QHBoxLayout()
        self.recent_layout.setSpacing(4)

        # Add some initial recent colors
        recent_colors = RECENT_FILL_COLORS
        for color_hex in recent_colors:
            swatch = ColorSwatch(QColor(color_hex), size=20)
            swatch.colorSelected.connect(self.colorSelected)
            self.recent_layout.addWidget(swatch)
        self.recent_layout.addStretch()

        self.layout.addLayout(self.recent_layout)

        # Custom color button
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(separator)

        self.btn_custom = QPushButton(_t("Custom Color..."))
        self.btn_custom.clicked.connect(self._open_custom_color)
        self.layout.addWidget(self.btn_custom)

    def _open_custom_color(self):
        color = QColorDialog.getColor(Qt.GlobalColor.white, self)
        if color.isValid():
            self.colorSelected.emit(color)

def create_fill_color_menu(parent_button, callback):
    menu = QMenu(parent_button)
    popup = FillColorPopup()

    action = QWidgetAction(menu)
    action.setDefaultWidget(popup)
    menu.addAction(action)

    def on_color_selected(color):
        menu.close()
        callback(color)

    popup.colorSelected.connect(on_color_selected)
    return menu
