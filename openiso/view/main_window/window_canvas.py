#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""Canvas interaction mixin for SkeyEditor."""

from __future__ import annotations

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import Qt

from openiso.view.graphics.geometry_items import PointItem
from openiso.core.i18n import _t


class CanvasMixin:
    """Mixin providing keyboard shortcuts, canvas manipulation and transform helpers for SkeyEditor."""

    # -----------------------------------------------------------------
    # Keyboard events
    # -----------------------------------------------------------------

    def keyPressEvent(self, event):
        """Handles keyboard shortcuts and events."""
        modifiers = event.modifiers()
        key = event.key()
        text = event.text()

        if modifiers == Qt.KeyboardModifier.ControlModifier:
            if text == 'i':
                self.import_external_file(); return
            elif text == 'e':
                self.export_to_file(); return
            elif text == 's':
                self.save_current_skey(); return
            elif text == 'p':
                self.print_symbol(); return
            elif text == 'z':
                self.undo_last_action(); return
            elif text == 'y':
                self.redo_next_action(); return
            elif text == 'a':
                self.select_all_items(); return
            elif text == ',':
                self._on_settings_clicked(); return
            elif text == 'h':
                self._on_about_clicked(); return
            elif key == Qt.Key.Key_Plus or text == '+':
                self.zoom_in(); return
            elif key == Qt.Key.Key_Minus or text == '-':
                self.zoom_out(); return

        elif modifiers == Qt.KeyboardModifier.NoModifier:
            if text.lower() == 'l':
                self._on_draw_line_clicked(); return
            elif text.lower() == 'p':
                self._on_draw_polyline_clicked(); return
            elif text.lower() == 'r':
                self._on_draw_rect_clicked(); return
            elif text.lower() == 'c':
                self._on_draw_circle_clicked(); return
            elif text.lower() == 'f':
                self.fit_to_view(); return
            elif key == Qt.Key.Key_Home:
                self.reset_view(); return
            elif key == Qt.Key.Key_Delete:
                self.clear_canvas(); return

        if key == Qt.Key.Key_F1:
            self._on_help_clicked(); return

        if key == Qt.Key.Key_Escape:
            if hasattr(self.scene, 'selected_for_highlight'):
                for item in self.scene.selected_for_highlight:
                    if hasattr(item, '_original_pen'):
                        item.setPen(item._original_pen)
                        del item._original_pen
                    if hasattr(item, '_original_brush'):
                        item.setBrush(item._original_brush)
                        del item._original_brush
                self.scene.selected_for_highlight.clear()
            self.scene.clearSelection()
            QApplication.restoreOverrideCursor()
            self.scene.current_action = ""
            return

        QMainWindow.keyPressEvent(self, event)

    def _on_focus_item_changed(self, newItem, _oldItem, reason):
        """Slot to handle focus changes between items (currently a placeholder)."""
        if newItem and reason == Qt.FocusReason.MouseFocusReason:
            pass  # Item clicked

    # -----------------------------------------------------------------
    # Canvas helpers
    # -----------------------------------------------------------------

    def clear_canvas(self):
        """Removes all user-drawn graphical elements from the current editing session."""
        for item in self.scene.symbol_drawlist:
            self.scene.removeItem(item)
        self.scene.symbol_drawlist.clear()

    def select_all_items(self):
        """Select all items on the canvas."""
        self.scene.select_all_items()

    def clear_selection(self):
        """Clears current selection on the canvas."""
        if hasattr(self.scene, 'selected_for_highlight'):
            for item in self.scene.selected_for_highlight:
                if hasattr(item, '_original_pen'):
                    item.setPen(item._original_pen)
                    del item._original_pen
                if hasattr(item, '_original_brush'):
                    item.setBrush(item._original_brush)
                    del item._original_brush
            self.scene.selected_for_highlight.clear()
        self.scene.clearSelection()
        return "Выделение снято"

    # -----------------------------------------------------------------
    # Undo / redo stubs
    # -----------------------------------------------------------------

    def undo_last_action(self):
        """Reverts the last drawing or editing operation performed."""
        print("Undo clicked")

    def redo_next_action(self):
        """Re-applies the operation that was previously undone."""
        print("Redo clicked")

    # -----------------------------------------------------------------
    # Transform operations
    # -----------------------------------------------------------------

    def move_element(self, axis, value):
        """Moves selected elements by a specific value along X or Y axis."""
        dx = value if axis == "X" else 0
        dy = -value if axis == "Y" else 0  # Y is inverted in Qt
        dx *= 100
        dy *= 100

        moved_count = 0
        for item in self.scene.selectedItems():
            item.moveBy(dx, dy)
            moved_count += 1

        if moved_count > 0:
            return f"Перемещено {moved_count} элементов на {value} по {axis}"
        return "Нет выделенных элементов для перемещения"

    def rotate_element(self, angle):
        """Rotates selected elements on the canvas by a given angle."""
        try:
            angle = float(angle)
            items = self.scene.selectedItems()
            if not items:
                return "Нет выделенных элементов для поворота"
            for item in items:
                item.setRotation(item.rotation() + angle)
            return f"Элементы ({len(items)}) повернуты на {angle} градусов"
        except ValueError:
            return "Ошибка: Некорректный угол поворота"

    def scale_element(self, factor):
        """Scales selected elements on the canvas by a given factor."""
        try:
            factor = float(factor)
            items = self.scene.selectedItems()
            if not items:
                return "Нет выделенных элементов для масштабирования"
            for item in items:
                item.setScale(item.scale() * factor)
            msg = f"Элементы ({len(items)}) масштабированы с коэффициентом {factor}"
            self.status_bar_widget.showMessage(msg, 3000)
            return msg
        except ValueError:
            return "Ошибка: Некорректный коэффициент масштабирования"

    # -----------------------------------------------------------------
    # View zoom / fit
    # -----------------------------------------------------------------

    def zoom_in(self):
        """Zooms in on the view by 20%."""
        self.view_editor.scale(1.2, 1.2)
        self.status_bar_widget.showMessage(_t("Zoomed in"), 1500)

    def zoom_out(self):
        """Zooms out on the view by 20%."""
        self.view_editor.scale(1 / 1.2, 1 / 1.2)
        self.status_bar_widget.showMessage(_t("Zoomed out"), 1500)

    def fit_to_view(self):
        """Fits the entire scene to the view."""
        self.view_editor.fitInView(
            self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio
        )
        self.status_bar_widget.showMessage(_t("Fitted to view"), 1500)

    def reset_view(self):
        """Resets the view to the default zoom and position."""
        self.view_editor.resetTransform()
        self.view_editor.fitInView(
            self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio
        )
        self.status_bar_widget.showMessage(_t("View reset"), 1500)
