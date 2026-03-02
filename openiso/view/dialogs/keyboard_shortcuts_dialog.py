# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QFrame, QPushButton
)
from PyQt6.QtCore import Qt
from openiso.core.i18n import setup_i18n

_t = setup_i18n()


class KeyboardShortcutsDialog(QDialog):
    """
    GNOME/Adwaita-style keyboard shortcuts dialog with tabs.
    Each shortcut group is displayed in a separate tab.
    """

    def __init__(self, parent=None, shortcuts_data=None):
        super().__init__(parent)

        self.setObjectName("KeyboardShortcutsDialog")
        self.setWindowTitle(_t("Keyboard Shortcuts"))
        self.setMinimumSize(700, 600)
        self.setStyleSheet(self._stylesheet())

        # Use default shortcuts if none provided
        self.shortcuts_data = shortcuts_data or self._default_shortcuts()

        self._build_ui()

    # -------
    #  Stylesheet
    # -------
    def _stylesheet(self):
        return """
        KeyboardShortcutsDialog {
            background-color: #ffffff;
        }

        QFrame[class="ShortcutRow"] {
            background-color: transparent;
            border: none;
            padding: 6px 0;
        }

        QLabel[class="ShortcutName"] {
            font-size: 14px;
            color: #1c1c1c;
            padding: 0px;
        }

        QLabel[class="ShortcutDescription"] {
            font-size: 10px;
            color: #6e6e6e;
            padding: 0px;
        }

        QLabel[class="KeyPill"] {
            font-size: 11px;
            font-weight: 500;
            color: #2e2e2e;
            background-color: #f7f7f7;
            border: 1px solid #cfcfcf;
            border-radius: 6px;
            padding: 3px 8px;
            min-width: 28px;
            text-align: center;
        }

        QTabWidget::pane {
            border: none;
        }

        QTabBar::tab {
            background-color: #f5f5f5;
            color: #333333;
            border: 1px solid #dcdcdc;
            border-bottom: none;
            padding: 8px 16px;
            margin-right: 2px;
            font-weight: 500;
        }

        QTabBar::tab:selected {
            background-color: #ffffff;
            border: 1px solid #dcdcdc;
            border-bottom: 1px solid #ffffff;
            color: #1c1c1c;
        }

        QTabBar::tab:hover:!selected {
            background-color: #fafafa;
        }
        """

    # -------
    #  UI
    # -------
    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(10, 10, 10, 10)
        main.setSpacing(15)

        # Create tabs widget
        tabs = QTabWidget()

        # Create a tab for each group
        for group in self.shortcuts_data:
            tab_content = self._create_tab_content(group["shortcuts"])
            tabs.addTab(tab_content, group["group"])

        main.addWidget(tabs)

        # Close button
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton(_t("Close"))
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        main.addLayout(btn_row)

    # -----
    #  Tab
    # -----
    def _create_tab_content(self, shortcuts):
        """Create content for a single tab."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        for name, desc, combo in shortcuts:
            layout.addWidget(self._create_row(name, desc, combo))

        layout.addStretch()
        return container

    # -------
    #  Row
    # -------
    def _create_row(self, name, desc, combo):
        row = QFrame()
        row.setProperty("class", "ShortcutRow")

        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(12)

        # Left side
        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(2)

        name_label = QLabel(name)
        name_label.setProperty("class", "ShortcutName")
        left.addWidget(name_label)

        if desc:
            desc_label = QLabel(desc)
            desc_label.setProperty("class", "ShortcutDescription")
            left.addWidget(desc_label)
        else:
            left.addStretch()

        layout.addLayout(left)
        layout.addStretch()

        # Right side: keys
        keys_layout = QHBoxLayout()
        keys_layout.setSpacing(4)

        for key in self._parse_combo(combo):
            pill = QLabel(key)
            pill.setProperty("class", "KeyPill")
            pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
            keys_layout.addWidget(pill)

        layout.addLayout(keys_layout)
        return row

    # -------
    #  Key parsing
    # -------
    def _parse_combo(self, combo):
        parts = combo.split('+')
        mapping = {
            "Ctrl": "Ctrl",
            "Shift": "Shift",
            "Alt": "Alt",
            "Super": "Super",
            "+": "+",
            "-": "-",
        }
        return [mapping.get(p.strip(), p.strip()) for p in parts]

    # -------
    #  Default shortcuts
    # -------
    def _default_shortcuts(self):
        return [
            {
                "group": _t("File Operations"),
                "shortcuts": [
                    (_t("Import File"), None, "Ctrl+I"),
                    (_t("Export File"), None, "Ctrl+E"),
                    (_t("Save"), None, "Ctrl+S"),
                    (_t("Print"), None, "Ctrl+P"),
                ]
            },
            {
                "group": _t("Editing"),
                "shortcuts": [
                    (_t("Undo"), None, "Ctrl+Z"),
                    (_t("Redo"), None, "Ctrl+Y"),
                    (_t("Select All"), None, "Ctrl+A"),
                    (_t("Clear Sheet"), None, "Delete"),
                ]
            },
            {
                "group": _t("Drawing Tools"),
                "shortcuts": [
                    (_t("Line Tool"), None, "L"),
                    (_t("Polyline Tool"), None, "P"),
                    (_t("Rectangle Tool"), None, "R"),
                    (_t("Circle Tool"), None, "C"),
                ]
            },
            {
                "group": _t("Application"),
                "shortcuts": [
                    (_t("Settings"), None, "Ctrl+,"),
                    (_t("Help"), None, "F1"),
                    (_t("About"), None, "Ctrl+H"),
                ]
            }
        ]
