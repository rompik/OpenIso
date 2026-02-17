# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QComboBox, QMenu, QWidgetAction, QFrame, QSpinBox
)
from PyQt6.QtGui import QColor, QPen, QBrush, QPainter, QPixmap, QIcon
from PyQt6.QtCore import Qt, pyqtSignal
from openiso.core.i18n import setup_i18n

_t = setup_i18n()

# Hatch pattern definitions (angle, spacing)
HATCH_PATTERNS = [
    ("None", None, None),
    ("Horizontal", 0, 5),
    ("Vertical", 90, 5),
    ("Diagonal /", 45, 5),
    ("Diagonal \\", 135, 5),
    ("Cross +", "cross", 5),
    ("Cross X", "cross_diagonal", 5),
    ("Dense Horizontal", 0, 3),
    ("Dense Vertical", 90, 3),
    ("Sparse Horizontal", 0, 10),
    ("Sparse Vertical", 90, 10),
    ("Brick", "brick", 8),
    ("Dots", "dots", 6),
]

class HatchSwatch(QPushButton):
    """Button showing a preview of a hatch pattern"""
    hatchSelected = pyqtSignal(str, object, int)  # name, angle/pattern, spacing

    def __init__(self, name, angle_or_pattern, spacing, size=48, parent=None):
        super().__init__(parent)
        self.name = name
        self.angle_or_pattern = angle_or_pattern
        self.spacing = spacing
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(lambda: self.hatchSelected.emit(self.name, self.angle_or_pattern, self.spacing))
        self.setProperty("class", "HatchSwatch")

        # Create preview icon
        self._create_preview_icon()

    def _create_preview_icon(self):
        """Create a visual preview of the hatch pattern"""
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.GlobalColor.white)

        if self.angle_or_pattern is None:
            # "None" pattern - just show white
            self.setIcon(QIcon(pixmap))
            return

        painter = QPainter(pixmap)
        pen = QPen(Qt.GlobalColor.black, 1)
        painter.setPen(pen)

        width, height = self.width(), self.height()

        if isinstance(self.angle_or_pattern, int):
            # Simple line pattern at an angle
            self._draw_line_pattern(painter, width, height, self.angle_or_pattern, self.spacing)
        elif self.angle_or_pattern == "cross":
            # Horizontal + Vertical cross
            self._draw_line_pattern(painter, width, height, 0, self.spacing)
            self._draw_line_pattern(painter, width, height, 90, self.spacing)
        elif self.angle_or_pattern == "cross_diagonal":
            # Diagonal cross (X pattern)
            self._draw_line_pattern(painter, width, height, 45, self.spacing)
            self._draw_line_pattern(painter, width, height, 135, self.spacing)
        elif self.angle_or_pattern == "brick":
            # Brick pattern
            self._draw_brick_pattern(painter, width, height, self.spacing)
        elif self.angle_or_pattern == "dots":
            # Dot pattern
            self._draw_dot_pattern(painter, width, height, self.spacing)

        painter.end()
        self.setIcon(QIcon(pixmap))

    def _draw_line_pattern(self, painter, width, height, angle, spacing):
        """Draw parallel lines at given angle"""
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
                painter.drawLine(0, int(start), int(start), 0)
                start += spacing
        elif angle == 135:
            # Diagonal lines (\)
            start = 0
            while start < width + height:
                painter.drawLine(0, int(start), int(start), height)
                start += spacing

    def _draw_brick_pattern(self, painter, width, height, spacing):
        """Draw brick-like pattern"""
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

    def _draw_dot_pattern(self, painter, width, height, spacing):
        """Draw dot pattern"""
        y = spacing // 2
        row = 0
        while y < height:
            x = spacing // 2 if row % 2 == 0 else spacing
            while x < width:
                painter.drawEllipse(int(x) - 1, int(y) - 1, 2, 2)
                x += spacing
            y += spacing
            row += 1

class HatchPopup(QWidget):
    hatchSelected = pyqtSignal(str, object, int)  # name, angle/pattern, spacing

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)

        # Label
        self.lbl_title = QLabel(_t("Hatch Pattern"))
        self.lbl_title.setProperty("class", "ColorPopupTitle")
        self.layout.addWidget(self.lbl_title)

        # Spacing control
        spacing_layout = QHBoxLayout()
        spacing_layout.addWidget(QLabel(_t("Spacing:")))
        self.spin_spacing = QSpinBox()
        self.spin_spacing.setRange(1, 50)
        self.spin_spacing.setValue(5)
        self.spin_spacing.setSuffix(" px")
        spacing_layout.addWidget(self.spin_spacing)
        spacing_layout.addStretch()
        self.layout.addLayout(spacing_layout)

        # Hatch pattern grid
        self.grid = QGridLayout()
        self.grid.setSpacing(4)

        cols = 3
        for i, (name, angle_or_pattern, default_spacing) in enumerate(HATCH_PATTERNS):
            r, c = divmod(i, cols)
            swatch = HatchSwatch(name, angle_or_pattern, default_spacing if default_spacing else 5)
            swatch.hatchSelected.connect(self._on_hatch_selected)
            self.grid.addWidget(swatch, r, c)

        self.layout.addLayout(self.grid)

        # Add stretch at bottom
        self.layout.addStretch()

    def _on_hatch_selected(self, name, angle_or_pattern, _default_spacing):
        """Emit with current spacing value from spinbox"""
        spacing = self.spin_spacing.value()
        self.hatchSelected.emit(name, angle_or_pattern, spacing)

def create_hatch_menu(parent_button, callback):
    """Create a menu with hatch pattern selection widget

    Args:
        parent_button: The button to attach the menu to
        callback: Function to call when hatch is selected,
                 signature: callback(name, angle_or_pattern, spacing)
    """
    menu = QMenu(parent_button)
    popup = HatchPopup()

    action = QWidgetAction(menu)
    action.setDefaultWidget(popup)
    menu.addAction(action)

    def on_hatch_selected(name, angle_or_pattern, spacing):
        menu.close()
        callback(name, angle_or_pattern, spacing)

    popup.hatchSelected.connect(on_hatch_selected)
    return menu
