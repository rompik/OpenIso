# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import os

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QMenu,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)

from openiso.view.base_classes.base_popup_menu_item import BaseMenuPopupItem


class BasePopupMenuGrouped(QWidget):
    """Popup containing multiple sections """
    selected = pyqtSignal(str, str) # (category, name)

    def __init__(self, title, groups_dict, icons_path, columns=5, parent=None):
        super().__init__(parent)
        #self.setFixedWidth(400)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Main Title
        lbl_main = QLabel(title)
        lbl_main.setProperty("class", "BasePopupMenuTitle")
        main_layout.addWidget(lbl_main)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setMaximumHeight(600)

        container = QWidget()
        self.sections_layout = QVBoxLayout(container)
        self.sections_layout.setSpacing(5)
        self.sections_layout.setContentsMargins(0, 0, 0, 0)

        # Create sections based on the dictionary
        for group_name, items in groups_dict.items():
            self.sections_layout.addWidget(self._create_section(group_name, items, icons_path, columns))

        self.scroll_area.setWidget(container)
        main_layout.addWidget(self.scroll_area)

    def _create_section(self, name, items, icons_path, columns):
        """Creates a gray-background frame for a group of items."""
        frame = QFrame()
        frame.setProperty("class", "BasePopupMenuSection")

        layout = QVBoxLayout(frame)

        # Section Title (e.g., 'Arrive Point')
        title = QLabel(name)
        title.setWordWrap(True)
        title.setProperty("class", "BasePopupMenuSectionTitle")
        layout.addWidget(title)

        grid_widget = QWidget()
        grid_widget.setProperty("class", "BasePopupMenuGrid")
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 5, 0, 5)
        grid.setHorizontalSpacing(4)
        grid.setVerticalSpacing(4)

        section_items = self._normalize_items(items)
        item_width, effective_columns = self._compute_layout_metrics(section_items, columns)

        for i, (item_key, item_label, icon_file) in enumerate(section_items):
            row, col = divmod(i, effective_columns)
            path = os.path.join(icons_path, icon_file)

            btn = BaseMenuPopupItem(
                name,
                item_label,
                path,
                item_width=item_width,
            )
            btn.item_value = item_key
            btn.item_selected.connect(self.selected.emit)
            grid.addWidget(btn, row, col)

        layout.addWidget(grid_widget)
        return frame

    def _normalize_items(self, items):
        """Normalize item definitions to (id, label, icon_file)."""
        normalized = []
        for item_key, item_data in items.items():
            item_label = str(item_key)
            icon_file = ""

            if isinstance(item_data, dict):
                item_label = str(item_data.get("label", item_label))
                icon_file = str(item_data.get("icon", ""))
            elif isinstance(item_data, (tuple, list)) and len(item_data) >= 2:
                item_label = str(item_data[0])
                icon_file = str(item_data[1])
            else:
                icon_file = str(item_data)

            normalized.append((str(item_key), item_label, icon_file))

        return normalized

    def _compute_layout_metrics(self, items, columns):
        """Pick item width and columns based on localized text length."""
        max_label_width = 0
        if items:
            metrics = QFontMetrics(self.font())
            max_label_width = max(metrics.horizontalAdvance(item_label) for _, item_label, _ in items)

        min_item_width = 76
        max_item_width = 132
        item_width = max(min_item_width, min(max_item_width, max_label_width + 16))

        max_section_width = 520
        max_columns_for_width = max(1, max_section_width // item_width)
        effective_columns = min(columns, max_columns_for_width)
        effective_columns = max(1, min(effective_columns, len(items) if items else 1))

        return item_width, effective_columns

    @staticmethod
    def create_menu(parent_widget, title, groups_dict, icons_path, callback):
        menu = QMenu(parent_widget)
        popup = BasePopupMenuGrouped(title, groups_dict, icons_path)

        action = QWidgetAction(menu)
        action.setDefaultWidget(popup)
        menu.addAction(action)

        popup.selected.connect(lambda cat, name: [callback(cat, name), menu.close()])
        return menu
