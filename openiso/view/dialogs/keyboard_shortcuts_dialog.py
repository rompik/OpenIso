# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from openiso.core.i18n import setup_i18n

_t = setup_i18n()


class ShortcutRow(QFrame):
    """One shortcut and the normalized text used to find it."""

    def __init__(self, name, description, combo, parent=None):
        super().__init__(parent)
        self.setProperty("class", "ShortcutRow")
        self.search_text = " ".join((name, description or "", combo)).casefold()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(16)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(3)
        name_label = QLabel(name)
        name_label.setProperty("class", "ShortcutName")
        text_layout.addWidget(name_label)
        if description:
            description_label = QLabel(description)
            description_label.setProperty("class", "ShortcutDescription")
            text_layout.addWidget(description_label)
        layout.addLayout(text_layout)
        layout.addStretch(1)

        for key in _parse_combo(combo):
            key_label = QLabel(key)
            key_label.setProperty("class", "KeyPill")
            key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(key_label)


class ShortcutGroup(QFrame):
    """A titled collection of shortcut rows."""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setProperty("class", "ShortcutGroup")
        self.rows = []
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 12)
        self._layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setProperty("class", "ShortcutGroupTitle")
        self._layout.addWidget(title_label)

    def add_shortcut(self, name, description, combo):
        row = ShortcutRow(name, description, combo, self)
        self.rows.append(row)
        self._layout.addWidget(row)
        return row

    def filter_rows(self, matching_rows):
        has_match = False
        for row in self.rows:
            visible = row in matching_rows
            row.setVisible(visible)
            has_match = has_match or visible
        self.setVisible(has_match)
        return has_match


def _parse_combo(combo):
    return [part.strip() for part in combo.split("+") if part.strip()]


class KeyboardShortcutsDialog(QDialog):
    def __init__(self, parent=None, shortcuts_data=None):
        super().__init__(parent)

        self.setObjectName("KeyboardShortcutsDialog")
        self.setWindowTitle(_t("Keyboard Shortcuts"))
        self.setMinimumSize(700, 520)
        self.resize(820, 620)
        dialog_font = QFont()
        dialog_font.setFamilies(["Cantarell", "Inter", "Segoe UI", "sans-serif"])
        self.setFont(dialog_font)
        self.setStyleSheet(self._stylesheet())

        initial_sections = list(shortcuts_data) if shortcuts_data is not None else self._default_shortcuts()
        self.shortcuts_data = []
        self._selected_section = 0
        self._section_pages = []
        self._search_groups = []
        self._search_index = []
        self._build_ui()
        for section in initial_sections:
            self.add_section(section["group"], section["shortcuts"])
        if self.section_list.count():
            self.section_list.setCurrentRow(0)
            self._select_section(0)

    def _stylesheet(self):
        return """
        KeyboardShortcutsDialog {
            background-color: #242424;
            color: #ffffff;
            font-family: "Cantarell", "Inter", "Segoe UI", sans-serif;
            border-radius: 12px;
        }
        QLineEdit#ShortcutSearch {
            color: #ffffff;
            background-color: #2f2f2f;
            border: 2px solid transparent;
            border-radius: 8px;
            padding: 8px 12px;
            selection-background-color: #3584e4;
        }
        QLineEdit#ShortcutSearch:focus { border: 2px solid #3584e4; }
        QScrollArea { background-color: #242424; border: none; }
        QScrollArea QWidget { background-color: transparent; }
        QListWidget#ShortcutSections {
            background-color: #2f2f2f;
            border: 1px solid #202020;
            border-radius: 8px;
            padding: 6px;
        }
        QListWidget#ShortcutSections::item {
            color: #ffffff;
            padding: 8px 12px;
            border-radius: 8px;
            margin: 2px;
        }
        QListWidget#ShortcutSections::item:hover:!selected {
            background-color: rgba(255, 255, 255, 0.07);
        }
        QListWidget#ShortcutSections::item:selected {
            color: #ffffff;
            background-color: #3584e4;
        }
        QFrame[class="ShortcutGroup"] {
            background-color: #2f2f2f;
            border: 1px solid #202020;
            border-radius: 12px;
        }
        QLabel[class="ShortcutGroupTitle"] {
            color: #9a9a9a;
            font-size: 12px;
            font-weight: bold;
            padding: 8px 10px 4px;
        }
        QFrame[class="ShortcutRow"] { background-color: transparent; border: none; }
        QLabel[class="ShortcutName"] {
            color: #ffffff;
            font-size: 14px;
            font-weight: normal;
        }
        QLabel[class="ShortcutDescription"] {
            color: #9a9a9a;
            font-size: 12px;
            font-weight: normal;
        }
        QLabel[class="KeyPill"] {
            color: #ffffff;
            background-color: #3c3c3c;
            border: 1px solid #202020;
            border-radius: 6px;
            padding: 4px 8px;
            min-width: 24px;
            font-size: 13px;
            font-weight: bold;
        }
        QLabel[class="KeyPill"]:hover { background-color: #454545; }
        QLabel#EmptyStateIcon { color: #9a9a9a; font-size: 34px; }
        QLabel#EmptyStateText { color: #9a9a9a; font-size: 14px; }
        QPushButton {
            color: #ffffff;
            background-color: #3c3c3c;
            border: 1px solid #202020;
            border-radius: 8px;
            padding: 8px 16px;
        }
        QPushButton:hover { background-color: #454545; }
        """

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 14)
        main_layout.setSpacing(14)

        self.search_entry = QLineEdit(self)
        self.search_entry.setObjectName("ShortcutSearch")
        self.search_entry.setPlaceholderText("Поиск комбинаций клавиш...")
        self.search_entry.setClearButtonEnabled(True)
        self.search_entry.setMinimumHeight(42)
        search_palette = self.search_entry.palette()
        search_palette.setColor(search_palette.ColorRole.PlaceholderText, QColor("#9a9a9a"))
        self.search_entry.setPalette(search_palette)
        self.search_entry.textChanged.connect(self._filter_shortcuts)
        main_layout.addWidget(self.search_entry)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(14)
        self.section_list = QListWidget(self)
        self.section_list.setObjectName("ShortcutSections")
        self.section_list.setFixedWidth(176)
        self.section_list.currentRowChanged.connect(self._select_section)
        content_layout.addWidget(self.section_list)

        self.content_stack = QStackedWidget(self)
        self.content_stack.setObjectName("ShortcutContent")
        content_layout.addWidget(self.content_stack, 1)
        main_layout.addLayout(content_layout, 1)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        close_button = QPushButton(_t("Close"), self)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        main_layout.addLayout(button_layout)

        self.search_page = QWidget(self)
        search_layout = QVBoxLayout(self.search_page)
        search_layout.setContentsMargins(0, 0, 0, 0)
        self.search_results = QWidget()
        self.search_results_layout = QVBoxLayout(self.search_results)
        self.search_results_layout.setContentsMargins(4, 4, 4, 4)
        self.search_results_layout.setSpacing(10)
        self.search_scroll = QScrollArea()
        self.search_scroll.setWidgetResizable(True)
        self.search_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.search_scroll.setWidget(self.search_results)

        self.empty_state = QWidget()
        empty_layout = QVBoxLayout(self.empty_state)
        empty_layout.addStretch(1)
        empty_icon = QLabel("⌕")
        empty_icon.setObjectName("EmptyStateIcon")
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_icon)
        empty_text = QLabel("Ничего не найдено")
        empty_text.setObjectName("EmptyStateText")
        empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_text)
        empty_layout.addStretch(1)

        self.search_content = QStackedWidget()
        self.search_content.addWidget(self.search_scroll)
        self.search_content.addWidget(self.empty_state)
        search_layout.addWidget(self.search_content)
        self.content_stack.addWidget(self.search_page)

    def add_section(self, title, shortcuts):
        """Add a section of (action, description, key-combination) tuples."""
        section_data = {"group": title, "shortcuts": list(shortcuts)}
        section_index = len(self._section_pages)
        self.shortcuts_data.append(section_data)
        self.section_list.addItem(title)

        section_page = self._create_section_page(title, section_data["shortcuts"])
        self.content_stack.insertWidget(section_index, section_page)
        self._section_pages.append(section_page)

        search_group = ShortcutGroup(title, self.search_results)
        for name, description, combo in section_data["shortcuts"]:
            row = search_group.add_shortcut(name, description, combo)
            self._search_index.append({
                "search_text": row.search_text,
                "row": row,
                "section": search_group,
            })
        self.search_results_layout.addWidget(search_group)
        self._search_groups.append(search_group)

        if section_index == 0:
            self.section_list.setCurrentRow(0)
            self._select_section(0)
        if self.search_entry.text().strip():
            self._filter_shortcuts(self.search_entry.text())

    def _create_section_page(self, title, shortcuts):
        group = ShortcutGroup(title)
        for name, description, combo in shortcuts:
            group.add_shortcut(name, description, combo)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidget(group)
        return scroll_area

    def _select_section(self, row):
        if 0 <= row < len(self._section_pages):
            self._selected_section = row
            self.content_stack.setCurrentWidget(self._section_pages[row])

    def _filter_shortcuts(self, text):
        query = text.strip().casefold()
        if not query:
            self.section_list.show()
            if self._section_pages:
                self.content_stack.setCurrentWidget(self._section_pages[self._selected_section])
            else:
                self.content_stack.setCurrentWidget(self.search_page)
            return

        self.section_list.hide()
        self.content_stack.setCurrentWidget(self.search_page)
        matching_rows = {
            item["row"] for item in self._search_index if query in item["search_text"]
        }
        any_match = False
        for group in self._search_groups:
            any_match = group.filter_rows(matching_rows) or any_match
        self.search_content.setCurrentWidget(self.search_scroll if any_match else self.empty_state)

    def _parse_combo(self, combo):
        return _parse_combo(combo)

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


ShortcutsDialog = KeyboardShortcutsDialog
