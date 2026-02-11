# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import math
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsRectItem,
    QGraphicsPolygonItem, QGraphicsPathItem
)
from PyQt6.QtGui import QPen, QPainter, QPolygonF
from PyQt6.QtCore import Qt, QPointF
from openiso.core.constants import PREVIEW_WIDTH, PREVIEW_HEIGHT, SCENE_COLORS, POINT_COLORS
from openiso.view.geometry_items import ArrivePoint, LeavePoint, TeePoint, SpindlePoint

class PreviewWidget(QGroupBox):
    """
    Component for displaying an isometric preview of a Skey shape.
    """
    def __init__(self, title, parent=None):
        """
        Initialize the PreviewWidget.

        Args:
            title (str): Title of the group box.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(title, parent)
        self.setFixedSize(340, 250)
        self.vbox_lay_preview = QVBoxLayout()
        self.setLayout(self.vbox_lay_preview)

        self.scene_preview = QGraphicsScene(self)
        self.scene_preview.setSceneRect(0, 0, PREVIEW_WIDTH, PREVIEW_HEIGHT)
        self.view_preview = QGraphicsView(self.scene_preview, self)
        self.view_preview.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view_preview.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view_preview.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.vbox_lay_preview.addWidget(self.view_preview)

    def update_preview(self, symbol_drawlist, origin_x, origin_y):
        """
        Update the preview scene with an isometric view of the symbol.

        Clears the current preview and redraws all items from the drawlist
        using isometric projection and appropriate scaling.

        Args:
            symbol_drawlist (list): List of QGraphicsItem primitive objects.
            origin_x (float): X-coordinate of the symbol's origin.
            origin_y (float): Y-coordinate of the symbol's origin.
        """
        self.scene_preview.clear()

        points = self._collect_preview_points(symbol_drawlist, origin_x, origin_y)
        if not points:
            return

        scale, center_x, center_y = self._calculate_preview_params(points)

        pen = QPen(SCENE_COLORS["default_pen"])
        pen.setWidth(1)

        arrive_point_pos = None
        leave_point_pos = None

        # Draw all items except points, but record Arrive/Leave point positions
        for item in symbol_drawlist:
            if isinstance(item, ArrivePoint):
                x, y = item.x() - origin_x, item.y() - origin_y
                arrive_point_pos = self._to_preview_coord(x, y, scale, center_x, center_y)
            elif isinstance(item, LeavePoint):
                x, y = item.x() - origin_x, item.y() - origin_y
                leave_point_pos = self._to_preview_coord(x, y, scale, center_x, center_y)
            elif isinstance(item, (TeePoint, SpindlePoint)):
                continue  # Do not draw points in preview
            elif isinstance(item, QGraphicsLineItem):
                self._draw_preview_line(item, scale, center_x, center_y, pen, origin_x, origin_y)
            elif isinstance(item, QGraphicsRectItem):
                self._draw_preview_rect(item, scale, center_x, center_y, pen, origin_x, origin_y)
            elif isinstance(item, QGraphicsPolygonItem):
                self._draw_preview_polygon(item, scale, center_x, center_y, pen, origin_x, origin_y)
            elif isinstance(item, QGraphicsPathItem):
                self._draw_preview_path(item, scale, center_x, center_y, pen, origin_x, origin_y)

        # Draw line from outside to ArrivePoint (using same color as editor)
        if arrive_point_pos:
            ax, ay = arrive_point_pos
            cx, cy = PREVIEW_WIDTH / 2, PREVIEW_HEIGHT / 2
            dx, dy = ax - cx, ay - cy
            length = (dx ** 2 + dy ** 2) ** 0.5
            if length == 0:
                dx, dy = 0, -1
                length = 1
            dx, dy = dx / length, dy / length
            start_x = ax - dx * 30
            start_y = ay - dy * 30
            preview_line = QGraphicsLineItem(start_x, start_y, ax, ay)
            preview_line.setPen(QPen(POINT_COLORS["arrive"], 2, Qt.PenStyle.SolidLine))
            self.scene_preview.addItem(preview_line)

        # Draw line from LeavePoint to outside (using same color as editor)
        if leave_point_pos:
            lx, ly = leave_point_pos
            cx, cy = PREVIEW_WIDTH / 2, PREVIEW_HEIGHT / 2
            dx, dy = lx - cx, ly - cy
            length = (dx ** 2 + dy ** 2) ** 0.5
            if length == 0:
                dx, dy = 0, 1
                length = 1
            dx, dy = dx / length, dy / length
            end_x = lx + dx * 30
            end_y = ly + dy * 30
            preview_line = QGraphicsLineItem(lx, ly, end_x, end_y)
            preview_line.setPen(QPen(POINT_COLORS["leave"], 2, Qt.PenStyle.SolidLine))
            self.scene_preview.addItem(preview_line)

    def _to_isometric(self, x, y):
        """
        Convert 2D coordinates to isometric projection.

        Args:
            x (float): 2D X-coordinate.
            y (float): 2D Y-coordinate.

        Returns:
            tuple: (iso_x, iso_y) projected coordinates.
        """
        iso_angle = math.pi / 6
        iso_x = (x - y) * math.cos(iso_angle)
        iso_y = (x + y) * math.sin(iso_angle)
        return iso_x, iso_y

    def _collect_preview_points(self, symbol_drawlist, origin_x, origin_y):
        """
        Gather all relevant points from the drawlist to calculate bounds.

        Args:
            symbol_drawlist (list): List of graphic items.
            origin_x (float): Reference origin X.
            origin_y (float): Reference origin Y.

        Returns:
            list: List of (x, y) relative tuples.
        """
        points = []
        for item in symbol_drawlist:
            if isinstance(item, (ArrivePoint, LeavePoint, TeePoint, SpindlePoint)):
                points.append((item.x() - origin_x, item.y() - origin_y))
            elif isinstance(item, QGraphicsLineItem):
                line = item.line()
                points.append((line.p1().x() - origin_x, line.p1().y() - origin_y))
                points.append((line.p2().x() - origin_x, line.p2().y() - origin_y))
            elif isinstance(item, QGraphicsRectItem):
                rect = item.rect()
                x, y = rect.x() - origin_x, rect.y() - origin_y
                points.append((x, y))
                points.append((x + rect.width(), y + rect.height()))
            elif isinstance(item, QGraphicsPolygonItem):
                polygon = item.polygon()
                for i in range(polygon.count()):
                    point = polygon.at(i)
                    points.append((point.x() - origin_x, point.y() - origin_y))
        return points

    def _calculate_preview_params(self, points):
        """
        Calculate scaling and centering parameters for the preview.

        Args:
            points (list): List of 2D points in the symbol.

        Returns:
            tuple: (scale, center_x, center_y) where scale is the zoom factor
                  and (center_x, center_y) is the centroid in isometric space.
        """
        iso_points = [self._to_isometric(x, y) for x, y in points]
        min_x = min(p[0] for p in iso_points)
        max_x = max(p[0] for p in iso_points)
        min_y = min(p[1] for p in iso_points)
        max_y = max(p[1] for p in iso_points)

        width = max(max_x - min_x, 1)
        height = max(max_y - min_y, 1)
        scale = min((PREVIEW_WIDTH - 40) / width, (PREVIEW_HEIGHT - 60) / height) * 0.8
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        return scale, center_x, center_y

    def _to_preview_coord(self, x, y, scale, center_x, center_y):
        """
        Map 2D symbol coordinates to 2D preview widget coordinates.

        Args:
            x, y: Original coordinates.
            scale: Calculated preview scale.
            center_x, center_y: Center of the symbol in isometric space.

        Returns:
            tuple: (px, py) coordinates in the preview scene.
        """
        preview_cx, preview_cy = PREVIEW_WIDTH / 2, PREVIEW_HEIGHT / 2
        iso_x, iso_y = self._to_isometric(x, y)
        px = preview_cx + (iso_x - center_x) * scale
        py = preview_cy + (iso_y - center_y) * scale
        return px, py

    def _draw_preview_line(self, item, scale, center_x, center_y, pen, origin_x, origin_y):
        """Draw a line primitive in the preview scene."""
        line = item.line()
        px1, py1 = self._to_preview_coord(line.p1().x() - origin_x, line.p1().y() - origin_y, scale, center_x, center_y)
        px2, py2 = self._to_preview_coord(line.p2().x() - origin_x, line.p2().y() - origin_y, scale, center_x, center_y)
        preview_line = QGraphicsLineItem(px1, py1, px2, py2)
        preview_line.setPen(pen)
        self.scene_preview.addItem(preview_line)

    def _draw_preview_rect(self, item, scale, center_x, center_y, pen, origin_x, origin_y):
        """Draw a rectangle primitive in the preview scene."""
        rect = item.rect()
        x, y = rect.x() - origin_x, rect.y() - origin_y
        w, h = rect.width(), rect.height()
        corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        preview_corners = [self._to_preview_coord(cx, cy, scale, center_x, center_y) for cx, cy in corners]
        for i in range(4):
            px1, py1 = preview_corners[i]
            px2, py2 = preview_corners[(i + 1) % 4]
            line = QGraphicsLineItem(px1, py1, px2, py2)
            line.setPen(pen)
            self.scene_preview.addItem(line)

    def _draw_preview_polygon(self, item, scale, center_x, center_y, pen, origin_x, origin_y):
        """Draw a polygon primitive in the preview scene."""
        polygon = item.polygon()
        if polygon.count() == 0:
            return
        iso_polygon = []
        for i in range(polygon.count()):
            point = polygon.at(i)
            px, py = self._to_preview_coord(point.x() - origin_x, point.y() - origin_y, scale, center_x, center_y)
            iso_polygon.append(QPointF(px, py))
        poly_item = QGraphicsPolygonItem(QPolygonF(iso_polygon))
        poly_item.setPen(pen)
        self.scene_preview.addItem(poly_item)

    def _draw_preview_path(self, item, scale, center_x, center_y, pen, origin_x, origin_y):
        """Draw a path primitive in the preview scene."""
        path = item.path()
        prev_point = None
        for t in range(21):
            point = path.pointAtPercent(t / 20.0)
            px, py = self._to_preview_coord(point.x() - origin_x, point.y() - origin_y, scale, center_x, center_y)
            if prev_point is not None:
                line = QGraphicsLineItem(prev_point[0], prev_point[1], px, py)
                line.setPen(pen)
                self.scene_preview.addItem(line)
            prev_point = (px, py)
