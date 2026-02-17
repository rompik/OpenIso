# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import os
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from openiso.core.constants import BUTTON_SIZE, ICONS
from openiso.core.i18n import setup_i18n

_t = setup_i18n()

class MenuToolbarWidget(QWidget):
    """
    Component for the menu and tool buttons panel.
    """
    def __init__(self, icons_path, parent=None):
        super().__init__(parent)
        self.setObjectName("MenuToolbar")
        self.icons_library_path = icons_path
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        self.setup_ui()

    def _create_tool_button(self, tooltip, icon_path=None, size=BUTTON_SIZE, text=None, icon_size=None):
        btn = QPushButton()
        if text:
            btn.setText(text)
        if tooltip:
            btn.setToolTip(_t(tooltip))
        if icon_path:
            icon_full_path = os.path.join(self.icons_library_path, icon_path)
            if os.path.exists(icon_full_path):
                btn.setIcon(QIcon(icon_full_path))

        actual_icon_size = icon_size if icon_size is not None else size
        btn.setIconSize(QSize(actual_icon_size, actual_icon_size))
        btn.setFixedSize(size, size)
        return btn

    def setup_ui(self):
        # File operations
        self.btn_import = self._create_tool_button("Import File", icon_path=ICONS["import"], text="")
        self.btn_export = self._create_tool_button("Export File", icon_path=ICONS["export"], text="")
        self.btn_print = self._create_tool_button("Print", icon_path=ICONS["print"])
        self.btn_save = self._create_tool_button("Save", icon_path=ICONS["save"])

        self.btn_import_from_ascii = self._create_tool_button("Import from ASCII", text="ASC")
        self.btn_import_from_idf = self._create_tool_button("Import from IDF", text="IDF")

        # System operations
        self.btn_settings = self._create_tool_button("Settings", icon_path=ICONS["settings"], text="")
        self.btn_keyboard_shortcuts = self._create_tool_button("Keyboard Shortcuts", icon_path=ICONS["keyboard"], text="")
        self.btn_help = self._create_tool_button("Help", icon_path=ICONS["help"], text="")
        self.btn_about = self._create_tool_button("About", icon_path=ICONS["about"], text="")

        self.layout.addWidget(self.btn_import)
        self.layout.addWidget(self.btn_export)
        self.layout.addWidget(self.btn_print)
        self.layout.addWidget(self.btn_save)
        #self.layout.addWidget(self.btn_import_from_ascii)
        #self.layout.addWidget(self.btn_import_from_idf)


        self.layout.addStretch()

        self.layout.addWidget(self.btn_settings)
        self.layout.addWidget(self.btn_keyboard_shortcuts)
        self.layout.addWidget(self.btn_help)
        self.layout.addWidget(self.btn_about)

    def update_translations(self, _t):
        self.btn_import.setToolTip(_t("Import File"))
        self.btn_export.setToolTip(_t("Export File"))
        self.btn_print.setToolTip(_t("Print"))
        self.btn_save.setToolTip(_t("Save"))
        self.btn_import_from_ascii.setToolTip(_t("Import of Skeys from ASCII file ( Intergraph )"))
        self.btn_import_from_idf.setToolTip(_t("Import Skeys from IDF file ( AVEVA )"))
        self.btn_settings.setToolTip(_t("Settings"))
        self.btn_keyboard_shortcuts.setToolTip(_t("Keyboard Shortcuts"))
        self.btn_help.setToolTip(_t("Help"))
        self.btn_about.setToolTip(_t("About"))
