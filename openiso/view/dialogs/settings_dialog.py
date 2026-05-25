# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QColorDialog,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from openiso.core.constants import (
    AVAILABLE_LANGUAGES,
    DEFAULT_ISO_VIEW,
    ISO_VIEW_NAMES,
)
from openiso.core.i18n import get_current_language, setup_i18n
from openiso.model.enums import IsometricView
from openiso.view.ui_constants import (
    POINT_COLORS,
    reset_point_colors,
)


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
        self._main_window = parent
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

        self.groupPreview = QGroupBox(self._t("Preview"))
        preview_layout = QVBoxLayout(self.groupPreview)

        self.preview_button_row = QHBoxLayout()
        self.chkPreviewVisible = QCheckBox(self._t("Show Preview"))
        self.chkPreviewVisible.toggled.connect(self._toggle_preview_visibility)
        self.preview_button_row.addWidget(self.chkPreviewVisible)
        self.preview_button_row.addStretch()
        preview_layout.addLayout(self.preview_button_row)

        self.preview_opacity_row = QHBoxLayout()
        self.lblPreviewOpacity = QLabel(self._t("Transparency:"))
        self.sliderPreviewOpacity = QSlider(Qt.Orientation.Horizontal)
        self.sliderPreviewOpacity.setRange(0, 100)
        self.sliderPreviewOpacity.setTickInterval(10)
        self.sliderPreviewOpacity.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sliderPreviewOpacity.valueChanged.connect(self._on_preview_opacity_changed)
        self.lblPreviewOpacityValue = QLabel("")

        self.preview_opacity_row.addWidget(self.lblPreviewOpacity)
        self.preview_opacity_row.addWidget(self.sliderPreviewOpacity)
        self.preview_opacity_row.addWidget(self.lblPreviewOpacityValue)
        preview_layout.addLayout(self.preview_opacity_row)

        self._initialize_preview_controls()
        content_layout.addWidget(self.groupPreview)

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

    def _get_preview_overlay(self):
        main_window = getattr(self, "_main_window", None)
        if main_window is None:
            return None
        return getattr(main_window, "overlay_preview_widget", None)

    def _initialize_preview_controls(self):
        overlay = self._get_preview_overlay()
        visible = False
        opacity = 70

        if overlay is not None:
            visible = overlay.isVisible()
            effect = overlay.graphicsEffect()
            if effect is not None and hasattr(effect, "opacity"):
                opacity = max(0, min(100, int(round(effect.opacity() * 100))))

        self._preview_visible = visible
        self._preview_opacity = opacity

        self.chkPreviewVisible.setChecked(visible)
        self.sliderPreviewOpacity.setValue(opacity)
        self.lblPreviewOpacityValue.setText(f"{opacity}%")
        self._original_preview_visible = visible
        self._original_preview_opacity = opacity

    def _toggle_preview_visibility(self, checked):
        self._preview_visible = bool(checked)
        overlay = self._get_preview_overlay()
        if overlay is not None:
            overlay.setVisible(self._preview_visible)

    def _on_preview_opacity_changed(self, value):
        self._preview_opacity = value
        self.lblPreviewOpacityValue.setText(f"{value}%")

        main_window = getattr(self, "_main_window", None)
        if main_window is not None and hasattr(main_window, "set_overlay_preview_opacity"):
            main_window.set_overlay_preview_opacity(value / 100.0)

    def _restore_preview_state(self):
        self._preview_visible = getattr(self, "_original_preview_visible", False)
        self._preview_opacity = getattr(self, "_original_preview_opacity", 70)

        overlay = self._get_preview_overlay()
        if overlay is not None:
            overlay.setVisible(self._preview_visible)

        main_window = getattr(self, "_main_window", None)
        if main_window is not None and hasattr(main_window, "set_overlay_preview_opacity"):
            main_window.set_overlay_preview_opacity(self._preview_opacity / 100.0)

        self.chkPreviewVisible.setChecked(self._preview_visible)
        self.sliderPreviewOpacity.setValue(self._preview_opacity)
        self.lblPreviewOpacityValue.setText(f"{self._preview_opacity}%")

    def reject(self):
        self._restore_preview_state()
        super().reject()

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

        # Note: Preview widget now uses the same colors as connection points
        # (arrive and leave colors from POINT_COLORS)

    def reset_colors(self):
        """Reset all colors to defaults."""
        # Reset runtime adapter colors first, then refresh button views.
        reset_point_colors()

        for key, btn in self.color_buttons['point'].items():
            btn.color = QColor(POINT_COLORS[key])
            btn.update_color()

    def get_selected_language(self):
        """Returns the selected language code."""
        return self.cbLanguage.currentData()

    def get_selected_isometric_view(self):
        """Returns the selected isometric view."""
        return self.cbIsoView.currentData()

    def get_preview_visibility(self):
        """Returns the preview visibility state."""
        return getattr(self, "_preview_visible", False)

    def get_preview_opacity(self):
        """Returns the preview opacity as a 0.0-1.0 float."""
        return getattr(self, "_preview_opacity", 70) / 100.0

    def get_point_colors(self):
        """Returns dictionary of point colors."""
        return {key: btn.get_color() for key, btn in self.color_buttons['point'].items()}

    def get_scene_colors(self):
        """Scene colors are no longer configurable from settings dialog."""
        return {}
