# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import math

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QPainter, QPen, QPolygonF
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsLineItem,
    QGraphicsPathItem,
    QGraphicsPolygonItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QGroupBox,
    QVBoxLayout,
)

from openiso.core.constants import (
    DEFAULT_ISO_VIEW,
    PREVIEW_HEIGHT,
    PREVIEW_WIDTH,
)
from openiso.view.ui_constants import POINT_COLORS, SCENE_COLORS
from openiso.model.enums import IsometricView
from openiso.view.graphics.geometry_items import (
    ArrivePoint,
    LeavePoint,
    SpindlePoint,
    TeePoint,
)


class PreviewWidget(QGroupBox):
    """
    Component for displaying an isometric preview of a Skey shape.
    """
    def __init__(self, title, parent=None, *, widget_size=(340, 250), scene_size=(PREVIEW_WIDTH, PREVIEW_HEIGHT)):
        """
        Initialize the PreviewWidget.

        Args:
            title (str): Title of the group box.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(title, parent)
        self.preview_width, self.preview_height = scene_size
        self.setFixedSize(*widget_size)
        self.vbox_lay_preview = QVBoxLayout()
        self.setLayout(self.vbox_lay_preview)

        self.scene_preview = QGraphicsScene(self)
        self.scene_preview.setSceneRect(0, 0, self.preview_width, self.preview_height)
        self.view_preview = QGraphicsView(self.scene_preview, self)
        self.view_preview.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view_preview.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view_preview.setFrameShape(QFrame.Shape.NoFrame)
        self.view_preview.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view_preview.setStyleSheet("background: transparent; border: none;")
        self.view_preview.setBackgroundBrush(Qt.GlobalColor.transparent)
        self.scene_preview.setBackgroundBrush(Qt.GlobalColor.transparent)
        self.vbox_lay_preview.addWidget(self.view_preview)

        # Set default isometric view
        self.iso_view = DEFAULT_ISO_VIEW

    def set_isometric_view(self, view):
        """
        Set the isometric view direction.

        Args:
            view (IsometricView): The isometric view direction to use.
        """
        self.iso_view = view

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
        self._draw_iso_axes()

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
                x, y = item.scenePos().x() - origin_x, item.scenePos().y() - origin_y
                arrive_point_pos = self._to_preview_coord(x, y, scale, center_x, center_y)
            elif isinstance(item, LeavePoint):
                x, y = item.scenePos().x() - origin_x, item.scenePos().y() - origin_y
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

        # Direction of the isometric X axis in preview screen coords (unit vector)
        iso_dx, iso_dy = self._to_isometric(1, 0)

        # Arrive arrow: tip AT the arrive point, shaft along iso X direction
        if arrive_point_pos:
            ax, ay = arrive_point_pos
            self._draw_preview_arrow(ax - iso_dx * 28, ay - iso_dy * 28, ax, ay, POINT_COLORS["arrive"])

        # Leave arrow: tail AT the leave point, shaft along iso X direction
        if leave_point_pos:
            lx, ly = leave_point_pos
            self._draw_preview_arrow(lx, ly, lx + iso_dx * 28, ly + iso_dy * 28, POINT_COLORS["leave"])

    def _to_isometric(self, x, y):
        """
        Convert 2D coordinates to isometric projection based on current view.

        Args:
            x (float): 2D X-coordinate.
            y (float): 2D Y-coordinate.

        Returns:
            tuple: (iso_x, iso_y) projected coordinates.
        """
        iso_angle = math.pi / 6

        if self.iso_view == IsometricView.NE:
            # NE: canvas X (→) → lower-right on screen, canvas Y (↓) → lower-left on screen
            iso_x = (x - y) * math.cos(iso_angle)
            iso_y = (x + y) * math.sin(iso_angle)
        elif self.iso_view == IsometricView.NW:
            # NW (default): canvas X (→) → lower-left on screen, canvas Y (↓) → lower-right on screen
            iso_x = -(x - y) * math.cos(iso_angle)
            iso_y = (x + y) * math.sin(iso_angle)
        elif self.iso_view == IsometricView.SE:
            # SE: canvas X (→) → upper-right on screen, canvas Y (↓) → upper-left on screen (vertical flip of NE)
            iso_x = (x - y) * math.cos(iso_angle)
            iso_y = -(x + y) * math.sin(iso_angle)
        elif self.iso_view == IsometricView.SW:
            # SW: canvas X (→) → upper-left on screen, canvas Y (↓) → upper-right on screen (vertical flip of NW)
            iso_x = -(x - y) * math.cos(iso_angle)
            iso_y = -(x + y) * math.sin(iso_angle)
        else:
            # Fallback to NW
            iso_x = -(x - y) * math.cos(iso_angle)
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
                points.append((item.scenePos().x() - origin_x, item.scenePos().y() - origin_y))
            elif isinstance(item, QGraphicsLineItem):
                line = item.line()
                p1 = item.mapToScene(line.p1())
                p2 = item.mapToScene(line.p2())
                points.append((p1.x() - origin_x, p1.y() - origin_y))
                points.append((p2.x() - origin_x, p2.y() - origin_y))
            elif isinstance(item, QGraphicsRectItem):
                rect = item.rect()
                corners = [
                    rect.topLeft(),
                    rect.topRight(),
                    rect.bottomRight(),
                    rect.bottomLeft(),
                ]
                for corner in corners:
                    p = item.mapToScene(corner)
                    points.append((p.x() - origin_x, p.y() - origin_y))
            elif isinstance(item, QGraphicsPolygonItem):
                polygon = item.polygon()
                for i in range(polygon.count()):
                    p = item.mapToScene(polygon.at(i))
                    points.append((p.x() - origin_x, p.y() - origin_y))
            elif isinstance(item, QGraphicsPathItem):
                path = item.path()
                for t in range(41):
                    sample = path.pointAtPercent(t / 40.0)
                    p = item.mapToScene(sample)
                    points.append((p.x() - origin_x, p.y() - origin_y))
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

        # Keep a dynamic inner padding so large symbols do not stick to edges.
        pad_x = max(8.0, min(24.0, self.preview_width * 0.08))
        pad_y = max(8.0, min(24.0, self.preview_height * 0.08))
        available_width = max(1.0, self.preview_width - 2.0 * pad_x)
        available_height = max(1.0, self.preview_height - 2.0 * pad_y)
        scale = min(available_width / width, available_height / height)

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
        preview_cx, preview_cy = self.preview_width / 2, self.preview_height / 2
        iso_x, iso_y = self._to_isometric(x, y)
        px = preview_cx + (iso_x - center_x) * scale
        py = preview_cy + (iso_y - center_y) * scale
        return px, py

    def _draw_preview_line(self, item, scale, center_x, center_y, pen, origin_x, origin_y):
        """Draw a line primitive in the preview scene."""
        line = item.line()
        p1 = item.mapToScene(line.p1())
        p2 = item.mapToScene(line.p2())
        px1, py1 = self._to_preview_coord(p1.x() - origin_x, p1.y() - origin_y, scale, center_x, center_y)
        px2, py2 = self._to_preview_coord(p2.x() - origin_x, p2.y() - origin_y, scale, center_x, center_y)
        preview_line = QGraphicsLineItem(px1, py1, px2, py2)
        preview_line.setPen(pen)
        self.scene_preview.addItem(preview_line)

    def _draw_preview_rect(self, item, scale, center_x, center_y, pen, origin_x, origin_y):
        """Draw a rectangle primitive in the preview scene."""
        rect = item.rect()
        scene_corners = [
            item.mapToScene(rect.topLeft()),
            item.mapToScene(rect.topRight()),
            item.mapToScene(rect.bottomRight()),
            item.mapToScene(rect.bottomLeft()),
        ]
        preview_corners = [
            self._to_preview_coord(p.x() - origin_x, p.y() - origin_y, scale, center_x, center_y)
            for p in scene_corners
        ]
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
            point = item.mapToScene(polygon.at(i))
            px, py = self._to_preview_coord(point.x() - origin_x, point.y() - origin_y, scale, center_x, center_y)
            iso_polygon.append(QPointF(px, py))
        poly_item = QGraphicsPolygonItem(QPolygonF(iso_polygon))
        poly_item.setPen(pen)
        self.scene_preview.addItem(poly_item)

    def _draw_iso_axes(self):
        """Draw isometric X/Y/Z axis indicator anchored to the bottom-left corner of the preview."""
        arm = 24
        label_pad = 14   # extra space reserved for axis labels
        margin = 5      # minimum gap from widget edges

        cos30 = math.cos(math.pi / 6)
        sin30 = math.sin(math.pi / 6)

        if self.iso_view == IsometricView.NE:
            x_dir = (cos30, sin30)
            y_dir = (-cos30, sin30)
        elif self.iso_view == IsometricView.NW:
            x_dir = (-cos30, sin30)
            y_dir = (cos30, sin30)
        elif self.iso_view == IsometricView.SE:
            x_dir = (cos30, -sin30)
            y_dir = (-cos30, -sin30)
        elif self.iso_view == IsometricView.SW:
            x_dir = (-cos30, -sin30)
            y_dir = (cos30, -sin30)
        else:
            x_dir = (cos30, sin30)
            y_dir = (-cos30, sin30)

        z_dir = (0.0, -1.0)  # Z always points up on screen (elevation)

        dirs = [x_dir, y_dir, z_dir]

        # Bounding box of all arm+label extents relative to a local origin (0, 0)
        reach = arm + label_pad
        offsets_x = [0.0] + [d[0] * reach for d in dirs]
        offsets_y = [0.0] + [d[1] * reach for d in dirs]
        min_ox = min(offsets_x)
        max_oy = max(offsets_y)

        # Anchor: left extent at `margin`, bottom extent at `preview_height - margin`
        ox = margin - min_ox
        oy = self.preview_height - margin - max_oy

        font = QFont()
        font.setPointSize(7)
        font.setBold(True)

        head_len = 5.0
        head_angle = math.pi / 5

        for (dx, dy), hex_color, label in [
            (x_dir, "#D04040", "X"),
            (y_dir, "#40B040", "Y"),
            (z_dir, "#4080D0", "Z"),
        ]:
            color = QColor(hex_color)
            pen = QPen(color, 1.5, Qt.PenStyle.SolidLine)
            ex = ox + dx * arm
            ey = oy + dy * arm

            shaft = QGraphicsLineItem(ox, oy, ex, ey)
            shaft.setPen(pen)
            self.scene_preview.addItem(shaft)

            length = math.hypot(dx, dy)
            if length > 0:
                ux, uy = dx / length, dy / length
                for sign in (1, -1):
                    ax = ex - head_len * (ux * math.cos(head_angle) - sign * uy * math.sin(head_angle))
                    ay = ey - head_len * (uy * math.cos(head_angle) + sign * ux * math.sin(head_angle))
                    wing = QGraphicsLineItem(ex, ey, ax, ay)
                    wing.setPen(pen)
                    self.scene_preview.addItem(wing)

            text = QGraphicsTextItem(label)
            text.setFont(font)
            text.setDefaultTextColor(color)
            text.setPos(ex + dx * 2 - 4, ey + dy * 2 - 6)
            self.scene_preview.addItem(text)

    def _draw_preview_arrow(self, x1, y1, x2, y2, color):
        """Draw a line with an arrowhead at (x2, y2) in the given color."""
        arrow_pen = QPen(color, 2, Qt.PenStyle.SolidLine)

        # Shaft
        shaft = QGraphicsLineItem(x1, y1, x2, y2)
        shaft.setPen(arrow_pen)
        self.scene_preview.addItem(shaft)

        # Arrowhead: two short lines branching back from the tip
        head_len = 7.0
        head_angle = math.pi / 6  # 30°

        # Direction from start to end
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            return
        ux, uy = dx / length, dy / length

        for sign in (1, -1):
            ax = x2 - head_len * (ux * math.cos(head_angle) - sign * uy * math.sin(head_angle))
            ay = y2 - head_len * (uy * math.cos(head_angle) + sign * ux * math.sin(head_angle))
            wing = QGraphicsLineItem(x2, y2, ax, ay)
            wing.setPen(arrow_pen)
            self.scene_preview.addItem(wing)

    def _draw_preview_path(self, item, scale, center_x, center_y, pen, origin_x, origin_y):
        """Draw a path primitive in the preview scene."""
        path = item.path()
        prev_point = None
        for t in range(21):
            point = item.mapToScene(path.pointAtPercent(t / 20.0))
            px, py = self._to_preview_coord(point.x() - origin_x, point.y() - origin_y, scale, center_x, center_y)
            if prev_point is not None:
                line = QGraphicsLineItem(prev_point[0], prev_point[1], px, py)
                line.setPen(pen)
                self.scene_preview.addItem(line)
            prev_point = (px, py)
