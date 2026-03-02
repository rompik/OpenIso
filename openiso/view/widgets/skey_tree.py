# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import os
from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QMenu
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint
from openiso.core.i18n import setup_i18n
from openiso.core.constants import ICONS


class SkeyTree(QTreeWidget):
    """
    Internal TreeWidget for displaying and filtering Skeys.
    """
    def __init__(self, parent=None):
        """
        Initialize the SkeyTree.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        header = self.header()
        if header:
            header.setVisible(False)
        self.setUniformRowHeights(True)
        self.tree_root = None

    def build_tree(self, groups, expanded: bool = False):
        """
        Build the Skey hierarchy in the tree widget from the provided groups.

        Args:
            groups: The Skey groups data structure holding groups, subgroups, and skeys.
            expanded (bool): Whether to initiallly expand group and subgroup items.
        """
        _t = setup_i18n()
        self.clear()
        self.tree_root = QTreeWidgetItem(self)
        self.tree_root.setText(0, _t("Components"))
        self.tree_root.setExpanded(True)

        for skey_group in groups.get_groups():
            group_level = QTreeWidgetItem(self.tree_root)
            group_level.setExpanded(expanded)
            group_level.setText(0, _t(skey_group))
            group_level.setData(0, Qt.ItemDataRole.UserRole, skey_group)
            group_level.setIcon(0, QIcon())

            for skey_subgroup in groups.get_subgroups(skey_group):
                subgroup_level = QTreeWidgetItem(group_level)
                subgroup_level.setExpanded(expanded)
                subgroup_level.setText(0, _t(f"{skey_group}.{skey_subgroup}"))
                subgroup_level.setData(0, Qt.ItemDataRole.UserRole, skey_subgroup)

                for skey in groups.get_skeys(skey_group, skey_subgroup):
                    skey_level = QTreeWidgetItem(subgroup_level)
                    # Use lowercase for the i18n key path to match JSON structure
                    skey_i18n_path = f"{skey_group}.{skey_subgroup}.{skey.lower()}"
                    skey_level.setText(0, _t(skey_i18n_path))
                    skey_level.setData(0, Qt.ItemDataRole.UserRole, skey)
                subgroup_level.sortChildren(0, Qt.SortOrder.AscendingOrder)
            group_level.sortChildren(0, Qt.SortOrder.AscendingOrder)

        # Sort top-level groups by their translated names
        self.tree_root.sortChildren(0, Qt.SortOrder.AscendingOrder)

    def filter_items(self, search_text):
        """
        Filter the tree items based on the provided search text.

        The search is case-insensitive. If an item or any of its children match
        the search text, the item is shown and expanded. If the search text is empty,
        all items are shown and non-root items are collapsed.

        Args:
            search_text (str): The text to filter the tree items by.
        """
        search_text = search_text.strip().lower()
        root = self.invisibleRootItem()
        if root is not None:
            def filter_item(item):
                item_text = item.text(0).lower()
                # Also search in the raw key/ID stored in UserRole
                item_data = str(item.data(0, Qt.ItemDataRole.UserRole) or "").lower()

                # If search_text is empty, we show everything and return to default expansion
                if not search_text:
                    item.setHidden(False)
                    # For non-root items, collapse by default
                    if item != self.tree_root:
                        item.setExpanded(False)

                    for i in range(item.childCount()):
                        filter_item(item.child(i))
                    return True

                # Check if this item or any of its children match
                item_match = search_text in item_text or search_text in item_data
                any_child_match = False
                for i in range(item.childCount()):
                    if filter_item(item.child(i)):
                        any_child_match = True

                match = item_match or any_child_match
                item.setHidden(not match)

                # Expand item if it has matching children or is a match itself (to show its children)
                if match:
                    item.setExpanded(True)

                return match

            for i in range(root.childCount()):
                filter_item(root.child(i))

        # Ensure root is always visible and expanded
        if self.tree_root is not None:
            self.tree_root.setHidden(False)
            self.tree_root.setExpanded(True)

    def select_item_by_path(self, group_name, subgroup_name=None, skey_name=None):
        """
        Finds and selects an item in the tree by its names hierarchy.
        """
        if not self.tree_root or not group_name:
            return

        # 1. Find group
        for i in range(self.tree_root.childCount()):
            group_item = self.tree_root.child(i)
            if group_item and group_item.text(0) == group_name:
                if not subgroup_name:
                    self.setCurrentItem(group_item)
                    return group_item

                # 2. Find subgroup
                for j in range(group_item.childCount()):
                    subgroup_item = group_item.child(j)
                    if subgroup_item and subgroup_item.text(0) == subgroup_name:
                        if not skey_name:
                            self.setCurrentItem(subgroup_item)
                            return subgroup_item

                        # 3. Find skey
                        for k in range(subgroup_item.childCount()):
                            skey_item = subgroup_item.child(k)
                            if skey_item and skey_item.text(0) == skey_name:
                                self.setCurrentItem(skey_item)
                                return skey_item

                # If subgroup/skey not found, select group
                self.setCurrentItem(group_item)
                return group_item
        return None


class SkeyTreeView(QWidget):
    """
    Combined widget containing search filter and Skey tree.
    """
    current_item_changed = pyqtSignal(object, object)
    create_skey_requested = pyqtSignal()
    delete_skey_requested = pyqtSignal(str)

    def __init__(self, icons_path=None, parent=None):
        """
        Initialize the SkeyTreeView.

        Args:
            icons_path (str, optional): Path to icons library.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.icons_library_path = icons_path
        self.vbox_layout = QVBoxLayout(self)
        self.vbox_layout.setContentsMargins(0, 0, 0, 0)

        # Search bar layout
        self.search_layout = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.btn_filter_clear = QPushButton()
        if self.icons_library_path:
            icon_path = os.path.join(self.icons_library_path, ICONS["filter_clear"])
            if os.path.exists(icon_path):
                self.btn_filter_clear.setIcon(QIcon(icon_path))
                self.btn_filter_clear.setIconSize(QSize(24, 24))

        self.search_layout.addWidget(self.txt_search)
        self.search_layout.addWidget(self.btn_filter_clear)
        self.vbox_layout.addLayout(self.search_layout)

        # Tree widget
        self.tree = SkeyTree()
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.vbox_layout.addWidget(self.tree)

        # Connect signals
        self.txt_search.textChanged.connect(self._on_filter_text_changed)
        self.btn_filter_clear.clicked.connect(self._on_filter_clear_clicked)
        self.tree.currentItemChanged.connect(self.current_item_changed.emit)
        self.tree.customContextMenuRequested.connect(self._on_context_menu)

        # Initial translations
        self.update_translations(setup_i18n())

    def update_translations(self, _t):
        """
        Update the labels and tooltips of the internal widgets based on the current translation.
        """
        self.btn_filter_clear.setToolTip(_t("Clear Filter"))
        self.txt_search.setPlaceholderText(_t("Search..."))

    def _on_filter_text_changed(self, text):
        """Handles the text changed signal from the search line edit."""
        self.tree.filter_items(text)

    def _on_filter_clear_clicked(self):
        """Handles the clicked signal from the clear button."""
        self.txt_search.clear()
        self.tree.filter_items("")

    def _on_context_menu(self, position: QPoint):
        """Handles the custom context menu requested signal."""
        item = self.tree.itemAt(position)
        menu = QMenu(self)
        _t = setup_i18n()

        create_action = menu.addAction(_t("Create New Skey"))
        create_action.triggered.connect(lambda: self.create_skey_requested.emit())

        # Only show delete option if we right-clicked on a specific skey
        # Skeys are leaf items at level 3 (Root -> Group -> Subgroup -> Skey)
        if item and item.childCount() == 0 and item.parent() and item.parent().parent():
            # Use raw skey name from UserRole
            skey_name = item.data(0, Qt.ItemDataRole.UserRole)
            if not skey_name:
                skey_name = item.text(0)

            delete_action = menu.addAction(_t("Delete Skey") + f" '{item.text(0)}'")
            delete_action.triggered.connect(lambda: self.delete_skey_requested.emit(skey_name))

        menu.exec(self.tree.viewport().mapToGlobal(position))

    def build_tree(self, groups, expanded: bool = False):
        """Delegates tree building to the internal tree widget."""
        self.tree.build_tree(groups, expanded)

    def filter_items(self, search_text):
        """Sets the filter text and updates the tree."""
        self.txt_search.setText(search_text)
        self.tree.filter_items(search_text)

    def setCurrentItem(self, item):
        """Delegates setting current item to the internal tree widget."""
        self.tree.setCurrentItem(item)

    def select_item_by_path(self, group_name, subgroup_name=None, skey_name=None):
        """Selects an item in the tree by its names hierarchy."""
        return self.tree.select_item_by_path(group_name, subgroup_name, skey_name)

    def invisibleRootItem(self):
        """Returns the invisible root item from the internal tree widget."""
        return self.tree.invisibleRootItem()

    def setContextMenuPolicy(self, policy):
        """Overrides setContextMenuPolicy to apply it to the internal tree widget."""
        self.tree.setContextMenuPolicy(policy)

    @property
    def customContextMenuRequested(self):
        """Returns the signal for custom context menu from the internal tree widget."""
        return self.tree.customContextMenuRequested
