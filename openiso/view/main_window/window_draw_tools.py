#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""Draw tools mixin for SkeyEditor."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QApplication, QGraphicsItem, QInputDialog

from openiso.core.i18n import _t
from openiso.view.graphics.geometry_items import PointItem


class DrawToolsMixin:
    """Mixin providing draw tool actions for SkeyEditor."""

    # -----------------------------------------------------------------
    # Shape shortcut handlers
    # -----------------------------------------------------------------

    def _on_draw_rect_clicked(self):
        """Activates the tool to draw a centered rectangle on the canvas."""
        self._set_draw_action("draw_rect")

    def _on_draw_square_clicked(self):
        """Activates the tool to draw a square on the canvas."""
        self._set_draw_action("draw_square")

    def _on_draw_circle_clicked(self):
        """Activates the tool to draw a circle on the canvas."""
        self._set_draw_action("draw_circle")

    def _on_draw_diamond_clicked(self):
        """Activates the tool to draw a diamond on the canvas."""
        self._set_draw_action("draw_diamond")

    def _on_draw_triangle_clicked(self):
        """Activates the tool to draw a triangle on the canvas."""
        self._set_draw_action("draw_triangle")

    def _on_draw_cap_clicked(self):
        """Activates the tool to draw a cap on the canvas."""
        self._set_draw_action("draw_cap")

    def _on_draw_hexagon_clicked(self):
        """Activates the tool to draw a hexagon on the canvas."""
        self._set_draw_action("draw_hexagon")

    def _on_draw_pentagon_clicked(self):
        """Activates the tool to draw a pentagon on the canvas."""
        self._set_draw_action("draw_pentagon")

    def _on_draw_octagon_clicked(self):
        """Activates the tool to draw an octagon on the canvas."""
        self._set_draw_action("draw_octagon")

    def _on_draw_dodecagon_clicked(self):
        """Activates the tool to draw a dodecagon on the canvas."""
        self._set_draw_action("draw_dodecagon")

    # -----------------------------------------------------------------
    # Line tool menu handler
    # -----------------------------------------------------------------

    def _on_line_tool_selected(self, category, tool_name):
        """Handle line tool selection from grouped popup menu.

        Args:
            category: Group name (e.g., "Lines")
            tool_name: Selected tool name (e.g., "Line", "Polyline", etc.)
        """
        tool_map = {
            "Line": self._on_draw_line_clicked,
            "Polyline": self._on_draw_polyline_clicked,
            "Orthogonal Polyline": self._on_draw_polyline_orthogonal_clicked,
        }
        handler = tool_map.get(tool_name)
        if handler:
            handler()
        else:
            print(f"[warning] Unknown line tool: {tool_name}")

    # -----------------------------------------------------------------
    # Shape tool menu handler
    # -----------------------------------------------------------------

    def _on_shape_tool_selected(self, category, tool_name):
        """Handle shape tool selection from grouped popup menu.

        Args:
            category: Group name (e.g., "Basic Shapes", "Special Shapes")
            tool_name: Selected tool name (e.g., "Square", "Circle", etc.)
        """
        tool_map = {
            "Square": self._on_draw_square_clicked,
            "Rectangle": self._on_draw_rect_clicked,
            "Circle": self._on_draw_circle_clicked,
            "Triangle": self._on_draw_triangle_clicked,
            "Diamond": self._on_draw_diamond_clicked,
            "Cap": self._on_draw_cap_clicked,
            "Hexagon": self._on_draw_hexagon_clicked,
            "Pentagon": self._on_draw_pentagon_clicked,
            "Octagon": self._on_draw_octagon_clicked,
            "Dodecagon": self._on_draw_dodecagon_clicked,
        }
        handler = tool_map.get(tool_name)
        if handler:
            handler()
        else:
            print(f"[warning] Unknown shape tool: {tool_name}")

    # -----------------------------------------------------------------
    # Connection / spindle popup handlers
    # -----------------------------------------------------------------

    def _on_spindle_from_popup_selected(self, spindle_name):
        """Callback for spindle selection from the popup menu."""
        print(f"Spindle selected from popup: {spindle_name}")
        self.scene.last_selected_spindle = spindle_name
        self._on_draw_spindle_point_clicked()
        self.status_bar_widget.showMessage(
            _t("Spindle selected: {name}").format(name=spindle_name), 3000
        )

    def _on_connection_popup_selected(self, connection_type, action):
        """Callback for connection type selection from the popup menu."""
        print(f"[debug] Connection selected: type={connection_type}, action/method={action}")
        self.scene.last_selected_connection_type = connection_type

        if hasattr(self, action):
            method = getattr(self, action)
            if callable(method):
                method()
                print(f"[debug] Called method: {action}")
            else:
                print(f"[error] Symbol '{action}' is not callable")
        elif action.startswith("draw_"):
            self._set_draw_action(action)
            print(f"[debug] Fallback: Set draw action to {action}")
        else:
            print(f"[error] Unknown action or method: {action}")

        self.status_bar_widget.showMessage(
            _t("Connection point: {0} ({1})").format(_t(connection_type), connection_type), 3000
        )

    # -----------------------------------------------------------------
    # Point draw actions
    # -----------------------------------------------------------------

    def _on_draw_arrive_point_clicked(self):
        """Activates the tool to place an Arrive Point on the canvas."""
        self._set_draw_action("draw_arrive_point")

    def _on_draw_leave_point_clicked(self):
        """Activates the tool to place a Leave Point on the canvas."""
        self._set_draw_action("draw_leave_point")

    def _on_draw_tee_point_clicked(self):
        """Activates the tool to place a Tee Point on the canvas."""
        self._set_draw_action("draw_tee_point")

    def _on_draw_spindle_point_clicked(self):
        """Activates the tool to place a Spindle (Valve) Point on the canvas."""
        self._set_draw_action("draw_spindle_point")

    # -----------------------------------------------------------------
    # Line draw actions
    # -----------------------------------------------------------------

    def _on_draw_line_clicked(self):
        """Activates the tool to draw a straight line on the canvas."""
        self._set_draw_action("draw_line")

    def _on_draw_polyline_clicked(self):
        """Activates the polyline tool."""
        self.status_bar_widget.showMessage(
            _t("Polyline: Click to add points, right-click or Enter to finish."), 3000
        )
        self._set_draw_action("draw_polyline")

    def _on_draw_polyline_orthogonal_clicked(self):
        """Activates the orthogonal polyline tool."""
        self.status_bar_widget.showMessage(
            _t("Orthogonal Polyline: Click to add points, right-click or Enter to finish."), 3000
        )
        self._set_draw_action("draw_polyline_orthogonal")

    # -----------------------------------------------------------------
    # Core draw action setter
    # -----------------------------------------------------------------

    def _set_draw_action(self, action):
        """Sets the active drawing mode on the canvas and changes the mouse cursor to a crosshair."""
        QApplication.restoreOverrideCursor()
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.CrossCursor))
        self.scene.current_action = action
        for item in self.scene.symbol_drawlist:
            if not isinstance(item, PointItem):
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

    # -----------------------------------------------------------------
    # Selection / move / rotate / scale
    # -----------------------------------------------------------------

    def _on_select_tool_clicked(self):
        """Activates the selection tool for interacting with existing canvas elements."""
        QApplication.restoreOverrideCursor()
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.scene.current_action = "select_element"
        self.scene.clearSelection()
        if hasattr(self.scene, 'selected_for_highlight'):
            for item in self.scene.selected_for_highlight:
                if hasattr(item, '_original_pen'):
                    item.setPen(item._original_pen)
                    del item._original_pen
                if hasattr(item, '_original_brush'):
                    item.setBrush(item._original_brush)
                    del item._original_brush
            self.scene.selected_for_highlight.clear()
        for item in self.scene.symbol_drawlist:
            if not isinstance(item, PointItem):
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

    def _on_move_tool_clicked(self):
        """Activates the move tool to relocate elements on the canvas."""
        QApplication.restoreOverrideCursor()
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.SizeAllCursor))
        self.scene.current_action = "move_element"
        for item in self.scene.symbol_drawlist:
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

    def _on_rotate_tool_clicked(self):
        """Rotates selected elements on the canvas by 90 degrees."""
        self.rotate_element(90)

    def _on_scale_tool_clicked(self):
        """Opens a dialog to scale selected elements by a factor."""
        items = self.scene.selectedItems()
        if not items:
            self.status_bar_widget.showMessage(_t("No items selected to scale"), 3000)
            return
        scale, ok = QInputDialog.getDouble(
            self, _t("Scale Element"), _t("Scale Factor:"), 1.0, 0.01, 100.0, 2
        )
        if ok:
            self.scale_element(scale)
