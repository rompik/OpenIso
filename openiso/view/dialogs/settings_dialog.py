# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QDialogButtonBox, QGroupBox, QPushButton, QGridLayout,
    QScrollArea, QWidget, QColorDialog
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from openiso.core.constants import (
    AVAILABLE_LANGUAGES, POINT_COLORS, SCENE_COLORS,
    DEFAULT_ISO_VIEW, ISO_VIEW_NAMES
)
from openiso.model.enums import IsometricView
from openiso.core.i18n import setup_i18n, get_current_language

class ColorButton(QPushButton):
    """Button that displays and allows selecting a color."""
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = color if isinstance(color, QColor) else QColor(color)
        self.setFixedSize(80, 30)
        self.update_color()
        self.clicked.connect(self.choose_color)

    def update_color(self):
        """Update button appearance to show current color."""
        rgb = self.color.getRgb()[:3]
        # Calculate luminance to determine text color
        luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
        text_color = "#000000" if luminance > 0.5 else "#FFFFFF"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color.name()};
                color: {text_color};
                border: 1px solid #999;
                border-radius: 3px;
                font-size: 9pt;
            }}
            QPushButton:hover {{
                border: 2px solid #666;
            }}
        """)
        self.setText(self.color.name().upper())

    def choose_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(self.color, self)
        if color.isValid():
            self.color = color
            self.update_color()

    def get_color(self):
        """Return current color."""
        return self.color


class SettingsDialog(QDialog):
    """
    Settings dialog for application configuration.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._t = setup_i18n()
        self.setWindowTitle(self._t("Settings"))
        self.setMinimumSize(600, 500)

        # Store color buttons for retrieval
        self.color_buttons = {
            'point': {},
            'scene': {}
        }

        self.setupUi()

    def setupUi(self):
        layout = QVBoxLayout(self)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)

        # Language Settings Group
        self.groupI18n = QGroupBox(self._t("Language Settings"))
        i18n_layout = QVBoxLayout(self.groupI18n)

        lang_layout = QHBoxLayout()
        self.lblLanguage = QLabel(self._t("Select Program Language:"))
        self.cbLanguage = QComboBox()

        # Populate language combo
        current_lang = get_current_language()
        default_index = 0
        for i, (name, code) in enumerate(AVAILABLE_LANGUAGES):
            self.cbLanguage.addItem(f"{name} ({code.upper()})", code)
            if code == current_lang:
                default_index = i

        self.cbLanguage.setCurrentIndex(default_index)

        lang_layout.addWidget(self.lblLanguage)
        lang_layout.addWidget(self.cbLanguage)
        i18n_layout.addLayout(lang_layout)

        content_layout.addWidget(self.groupI18n)

        # Isometric View Settings Group
        self.groupIsoView = QGroupBox(self._t("Isometric View"))
        iso_view_layout = QVBoxLayout(self.groupIsoView)

        view_layout = QHBoxLayout()
        self.lblIsoView = QLabel(self._t("Select Isometric Direction:"))
        self.cbIsoView = QComboBox()

        # Populate isometric view combo
        for view in IsometricView:
            view_name = ISO_VIEW_NAMES.get(view, f"View {view}")
            self.cbIsoView.addItem(view_name, view)

        # Set default view
        self.cbIsoView.setCurrentIndex(DEFAULT_ISO_VIEW)

        view_layout.addWidget(self.lblIsoView)
        view_layout.addWidget(self.cbIsoView)
        iso_view_layout.addLayout(view_layout)

        content_layout.addWidget(self.groupIsoView)

        # Color Settings Groups (below Language Settings)
        self._add_color_groups(content_layout)

        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Standard buttons
        button_layout = QHBoxLayout()

        self.btn_reset = QPushButton(self._t("Reset to Defaults"))
        self.btn_reset.clicked.connect(self.reset_colors)
        button_layout.addWidget(self.btn_reset)

        button_layout.addStretch()

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        button_layout.addWidget(self.buttonBox)

        layout.addLayout(button_layout)

    def _add_color_groups(self, layout):
        """Add color settings groups below language settings."""
        # Point Colors Group
        point_group = QGroupBox(self._t("Connection Point Colors"))
        point_layout = QGridLayout(point_group)
        point_layout.setColumnStretch(2, 1)

        point_colors = [
            ("arrive", self._t("Arrive Point"), POINT_COLORS["arrive"]),
            ("leave", self._t("Leave Point"), POINT_COLORS["leave"]),
            ("tee", self._t("Tee Point"), POINT_COLORS["tee"]),
            ("spindle", self._t("Spindle Point"), POINT_COLORS["spindle"]),
        ]

        for row, (key, label, color) in enumerate(point_colors):
            lbl = QLabel(label + ":")
            btn = ColorButton(color)
            desc = QLabel(self._t("Color for connection point type"))
            desc.setProperty("class", "SettingsDescriptionText")

            point_layout.addWidget(lbl, row, 0)
            point_layout.addWidget(btn, row, 1)
            point_layout.addWidget(desc, row, 2)

            self.color_buttons['point'][key] = btn

        layout.addWidget(point_group)

        # Scene Colors Group
        scene_group = QGroupBox(self._t("Scene and Grid Colors"))
        scene_layout = QGridLayout(scene_group)
        scene_layout.setColumnStretch(2, 1)

        scene_colors = [
            ("background", self._t("Background"), SCENE_COLORS["background"], self._t("Scene background color")),
            ("sheet_border", self._t("Sheet Border"), SCENE_COLORS["sheet_border"], self._t("Border around drawing sheet")),
            ("grid_origin", self._t("Grid Origin"), SCENE_COLORS["grid_origin"], self._t("Origin axis lines")),
            ("grid_major", self._t("Major Grid"), SCENE_COLORS["grid_major"], self._t("Major grid lines (1.0 units)")),
            ("grid_middle", self._t("Middle Grid"), SCENE_COLORS["grid_middle"], self._t("Middle grid lines (0.5 units)")),
            ("grid_minor", self._t("Minor Grid"), SCENE_COLORS["grid_minor"], self._t("Minor grid lines (0.1 units)")),
            ("grid_label", self._t("Grid Labels"), SCENE_COLORS["grid_label"], self._t("Grid coordinate labels")),
            ("highlight", self._t("Selection Highlight"), SCENE_COLORS["highlight"], self._t("Selected items color")),
            ("default_pen", self._t("Default Pen"), SCENE_COLORS["default_pen"], self._t("Default drawing pen color")),
        ]

        for row, (key, label, color, desc_text) in enumerate(scene_colors):
            lbl = QLabel(label + ":")
            btn = ColorButton(color)
            desc = QLabel(desc_text)
            desc.setProperty("class", "SettingsDescriptionText")

            scene_layout.addWidget(lbl, row, 0)
            scene_layout.addWidget(btn, row, 1)
            scene_layout.addWidget(desc, row, 2)

            self.color_buttons['scene'][key] = btn

        layout.addWidget(scene_group)

        # Note: Preview widget now uses the same colors as connection points
        # (arrive and leave colors from POINT_COLORS)

    def reset_colors(self):
        """Reset all colors to defaults."""
        # Reset point colors
        defaults = {
            'arrive': QColor(51, 51, 255),
            'leave': QColor(255, 0, 0),
            'tee': QColor(255, 0, 255),
            'spindle': QColor(111, 0, 0),
        }
        for key, btn in self.color_buttons['point'].items():
            btn.color = defaults[key]
            btn.update_color()

        # Reset scene colors
        scene_defaults = {
            'background': QColor(255, 255, 255),
            'sheet_border': QColor(0, 0, 0),
            'grid_origin': QColor(100, 100, 100),
            'grid_major': QColor(180, 180, 180),
            'grid_middle': QColor(210, 210, 210),
            'grid_minor': QColor(230, 230, 230),
            'grid_label': QColor(100, 100, 100),
            'highlight': QColor(0, 200, 0),
            'default_pen': QColor(0, 0, 0),
        }
        for key, btn in self.color_buttons['scene'].items():
            btn.color = scene_defaults[key]
            btn.update_color()

    def get_selected_language(self):
        """Returns the selected language code."""
        return self.cbLanguage.currentData()

    def get_selected_isometric_view(self):
        """Returns the selected isometric view."""
        return self.cbIsoView.currentData()

    def get_point_colors(self):
        """Returns dictionary of point colors."""
        return {key: btn.get_color() for key, btn in self.color_buttons['point'].items()}

    def get_scene_colors(self):
        """Returns dictionary of scene colors."""
        return {key: btn.get_color() for key, btn in self.color_buttons['scene'].items()}
