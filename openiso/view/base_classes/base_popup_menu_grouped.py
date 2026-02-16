# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout,
    QLabel, QMenu, QWidgetAction, QFrame, QScrollArea
)
from PyQt6.QtCore import pyqtSignal

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
        title.setProperty("class", "BasePopupMenuSectionTitle")
        layout.addWidget(title)

        grid_widget = QWidget()
        grid_widget.setProperty("class", "BasePopupMenuGrid")
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 5, 0, 5)

        for i, (item_name, icon_file) in enumerate(items.items()):
            row, col = divmod(i, columns)
            path = os.path.join(icons_path, icon_file)

            btn = BaseMenuPopupItem(name, item_name, path)
            btn.item_selected.connect(self.selected.emit)
            grid.addWidget(btn, row, col)

        layout.addWidget(grid_widget)
        return frame

    @staticmethod
    def create_menu(parent_widget, title, groups_dict, icons_path, callback):
        menu = QMenu(parent_widget)
        popup = BasePopupMenuGrouped(title, groups_dict, icons_path)

        action = QWidgetAction(menu)
        action.setDefaultWidget(popup)
        menu.addAction(action)

        popup.selected.connect(lambda cat, name: [callback(cat, name), menu.close()])
        return menu
