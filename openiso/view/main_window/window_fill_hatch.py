#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""Fill and hatch mixin for SkeyEditor."""

from __future__ import annotations

from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsPathItem
from PyQt6.QtGui import QBrush, QPen, QPixmap, QPainter
from PyQt6.QtCore import Qt

from openiso.core.i18n import _t


class FillHatchMixin:
    """Mixin providing fill-color and hatch-pattern actions for SkeyEditor."""

    def _on_fill_color_selected(self, color):
        """Applies the selected fill color to all chosen closed primitives."""
        selected_items = self.scene.selectedItems()
        if not selected_items:
            self.status_bar_widget.showMessage(_t("No items selected to fill"), 3000)
            return
        for item in selected_items:
            if isinstance(item, (QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsPathItem)):
                item.setBrush(QBrush(color, Qt.BrushStyle.SolidPattern))
        self.status_bar_widget.showMessage(_t("Fill color applied"), 3000)

    def _on_hatch_selected(self, name, angle_or_pattern, spacing):
        """Applies the selected hatch pattern to all chosen closed primitives."""
        selected_items = self.scene.selectedItems()
        if not selected_items:
            self.status_bar_widget.showMessage(_t("No items selected for hatching"), 3000)
            return

        if name == "None":
            for item in selected_items:
                if isinstance(item, (QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsPathItem)):
                    item.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            self.status_bar_widget.showMessage(_t("Hatch cleared"), 3000)
            return

        for item in selected_items:
            if isinstance(item, (QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsPathItem)):
                brush = self._create_hatch_brush(angle_or_pattern, spacing)
                item.setBrush(brush)
        self.status_bar_widget.showMessage(_t(f"Hatch pattern '{name}' applied"), 3000)

    def _create_hatch_brush(self, angle_or_pattern, spacing):
        """Create a brush with the specified hatch pattern."""
        size = max(spacing * 4, 32)
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        pen = QPen(Qt.GlobalColor.black, 1)
        painter.setPen(pen)

        if isinstance(angle_or_pattern, int):
            self._draw_hatch_lines(painter, size, size, angle_or_pattern, spacing)
        elif angle_or_pattern == "cross":
            self._draw_hatch_lines(painter, size, size, 0, spacing)
            self._draw_hatch_lines(painter, size, size, 90, spacing)
        elif angle_or_pattern == "cross_diagonal":
            self._draw_hatch_lines(painter, size, size, 45, spacing)
            self._draw_hatch_lines(painter, size, size, 135, spacing)
        elif angle_or_pattern == "brick":
            self._draw_brick_hatch(painter, size, size, spacing)
        elif angle_or_pattern == "dots":
            self._draw_dot_hatch(painter, size, size, spacing)

        painter.end()
        return QBrush(pixmap)

    def _draw_hatch_lines(self, painter, width, height, angle, spacing):
        """Draw parallel lines at the given angle for a hatch pattern."""
        if angle == 0:
            y = 0
            while y < height:
                painter.drawLine(0, int(y), width, int(y))
                y += spacing
        elif angle == 90:
            x = 0
            while x < width:
                painter.drawLine(int(x), 0, int(x), height)
                x += spacing
        elif angle == 45:
            start = -width
            while start < width + height:
                painter.drawLine(0, int(start), int(min(start, width)), 0)
                painter.drawLine(int(max(0, start - height)), height, width, int(max(0, width + height - start)))
                start += spacing
        elif angle == 135:
            start = 0
            while start < width + height:
                painter.drawLine(0, int(min(start, height)), int(min(start, width)), 0)
                painter.drawLine(int(max(0, start - height)), height, width, int(max(0, width + height - start)))
                start += spacing

    def _draw_brick_hatch(self, painter, width, height, spacing):
        """Draw a brick-like hatch pattern."""
        y = 0
        offset = False
        while y < height:
            painter.drawLine(0, int(y), width, int(y))
            x = spacing // 2 if offset else 0
            while x < width:
                painter.drawLine(int(x), int(y), int(x), int(min(y + spacing, height)))
                x += spacing
            y += spacing
            offset = not offset

    def _draw_dot_hatch(self, painter, width, height, spacing):
        """Draw a dot hatch pattern."""
        y = spacing // 2
        row = 0
        while y < height:
            x = spacing // 2 if row % 2 == 0 else spacing
            while x < width:
                painter.drawEllipse(int(x) - 1, int(y) - 1, 2, 2)
                x += spacing
            y += spacing
            row += 1
