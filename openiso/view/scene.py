# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import math
from collections import namedtuple
from PyQt6.QtWidgets import (
    QGraphicsScene, QGraphicsLineItem, QGraphicsRectItem, QGraphicsEllipseItem,
    QGraphicsPolygonItem, QGraphicsSimpleTextItem, QGraphicsItem, QApplication,
    QGraphicsPathItem
)
from PyQt6.QtGui import (
    QPolygonF, QPen, QPainterPath, QTransform, QBrush
)
from PyQt6.QtCore import Qt, QPointF, pyqtSignal, QRectF
from openiso.core.constants import SHEET_SIZE, SCENE_COLORS
from openiso.view.geometry_items import ArrivePoint, LeavePoint, TeePoint, SpindlePoint


class ResizeHandle(QGraphicsRectItem):
    """A small marker at the edges of a primitive to resize it."""
    def __init__(self, parent_item, index, scene):
        super().__init__(QRectF(-4, -4, 8, 8), parent_item)
        self.parent_item = parent_item
        self.index = index
        self.scene_ref = scene
        self.setBrush(QBrush(SCENE_COLORS["background"]))
        self.setPen(QPen(SCENE_COLORS["sheet_border"], 1))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setZValue(1000)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        # Snap new position to grid
        pos = self.scene_ref.snap_to_grid(self.scenePos())
        # Update parent geometry
        self.scene_ref.update_item_geometry(self.parent_item, self.index, pos)
        # Snap handle itself to grid in parent coordinates
        self.setPos(self.parent_item.mapFromScene(pos))

    def mousePressEvent(self, event):
        self._before_state = self.scene_ref._capture_item_state(self.parent_item)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        after_state = self.scene_ref._capture_item_state(self.parent_item)
        if self._before_state is not None and after_state is not None:
            if self._before_state != after_state:
                self.scene_ref._push_undo_action(
                    "transform",
                    [self.parent_item],
                    before=[self._before_state],
                    after=[after_state]
                )
                self.scene_ref.symbol_changed.emit()
        self._before_state = None


class SheetLayout(QGraphicsScene):
    spindle_point_placed = pyqtSignal(str, QPointF)
    symbol_changed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor_coordinates = []
        self.symbol_drawlist_temp = []
        self.symbol_drawlist = []
        self.grid_drawlist = []
        self.last_selected_spindle = ""
        self.last_selected_connection_type = ""
        self.selection_handles = []
        self.selected_for_highlight = set()
        self.undo_stack = []
        self.redo_stack = []
        self._move_before_states = None

        # Pre-create reusable graphics items
        self.arrive_point = ArrivePoint()
        self.leave_point = LeavePoint()
        self.tee_point = TeePoint()
        self.spindle_point = SpindlePoint()
        self.line = QGraphicsLineItem()
        self.rect = QGraphicsRectItem()
        self.triangle = QGraphicsPolygonItem()
        self.cap = QGraphicsPathItem()
        self.hexagon = QGraphicsPolygonItem()

        # Sheet and grid settings
        self.sheet_width = SHEET_SIZE
        self.sheet_height = SHEET_SIZE
        self.step_x = 5
        self.step_y = 5
        self.origin_x = 0
        self.origin_y = 0

        self.current_action = None
        self.cursor_position = QPointF(0.0, 0.0)
        self.point_diameter = 5

        self.draw_grid()
        self.selectionChanged.connect(self.update_selection_handles)

        Primitive = namedtuple("Primitive", ["points_required", "draw_func"])

        self.primitives = {
            "draw_line": Primitive(2, self.draw_line),
            "draw_rect": Primitive(2, self.draw_rect),
            "draw_square": Primitive(2, self.draw_square),
            "draw_circle": Primitive(2, self.draw_circle),
            "draw_triangle": Primitive(3, self.draw_triangle),
            "draw_diamond": Primitive(2, self.draw_diamond),
            "draw_cap": Primitive(2, self.draw_cap),
            "draw_hexagon": Primitive(2, self.draw_hexagon),
            "draw_pentagon": Primitive(2, self.draw_pentagon),
            "draw_octagon": Primitive(2, self.draw_octagon),
            "draw_dodecagon": Primitive(2, self.draw_dodecagon),
            "draw_arrive_point": Primitive(1, self.draw_arrive_point),
            "draw_leave_point": Primitive(1, self.draw_leave_point),
            "draw_tee_point": Primitive(1, self.draw_tee_point),
            "draw_spindle_point": Primitive(1, self.draw_spindle_point),
        }

    def convert_to_relative_position(self, scene_position):
        # Use SHEET_SIZE for fixed coordinate system
        x = (scene_position.x() - SHEET_SIZE / 2) / (self.step_x * 20)
        y = (SHEET_SIZE / 2 - scene_position.y()) / (self.step_y * 20)
        return QPointF(round(x, 3), round(y, 3))

    def draw_grid(self):
        """Draws a hierarchical grid that is fixed at SHEET_SIZE."""
        width = SHEET_SIZE
        height = SHEET_SIZE

        # Center origin
        origin_x = width / 2
        origin_y = height / 2

        self.sheet_width = width
        self.sheet_height = height

        # Use a margin to ensure labels are visible and grid covers area
        margin = 100
        self.setSceneRect(-margin, -margin, width + 2 * margin, height + 2 * margin)
        self.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)

        # Clear existing grid
        for item in self.grid_drawlist:
            if item.scene() == self:
                self.removeItem(item)
        self.grid_drawlist.clear()

        # Define grid pens with hierarchy
        pen_origin = QPen(SCENE_COLORS["grid_origin"], 1.2, Qt.PenStyle.SolidLine)
        pen_major = QPen(SCENE_COLORS["grid_major"], 0.8, Qt.PenStyle.SolidLine)  # 1.0 units (100px)
        pen_middle = QPen(SCENE_COLORS["grid_middle"], 0.5, Qt.PenStyle.DashLine)  # 0.5 units (50px)
        pen_minor = QPen(SCENE_COLORS["grid_minor"], 0.3, Qt.PenStyle.SolidLine)  # 0.1 units (10px)

        # Draw Vertical Lines
        for x_px in range(0, int(width) + 1, 10):
            if abs(x_px - origin_x) < 1:  # Float comparison for center
                pen = pen_origin
            elif round(x_px - origin_x) % 100 == 0:
                pen = pen_major
            elif round(x_px - origin_x) % 50 == 0:
                pen = pen_middle
            else:
                pen = pen_minor

            line = self.addLine(x_px, 0, x_px, height, pen)
            if line:
                line.setZValue(-100)
                self.grid_drawlist.append(line)

            # Labels for major lines
            if round(x_px - origin_x) % 100 == 0:
                val = (x_px - origin_x) / 100
                label = QGraphicsSimpleTextItem(f"{val:.1f}")
                label.setBrush(QBrush(SCENE_COLORS["grid_label"]))
                label.setScale(0.8)
                br = label.boundingRect()
                label.setPos(x_px - br.width() * 0.8 / 2, height + 5)
                label.setZValue(-100)
                self.addItem(label)
                self.grid_drawlist.append(label)

        # Draw Horizontal Lines
        for y_px in range(0, int(height) + 1, 10):
            if abs(y_px - origin_y) < 1:
                pen = pen_origin
            elif round(y_px - origin_y) % 100 == 0:
                pen = pen_major
            elif round(y_px - origin_y) % 50 == 0:
                pen = pen_middle
            else:
                pen = pen_minor

            line = self.addLine(0, y_px, width, y_px, pen)
            if line:
                line.setZValue(-100)
                self.grid_drawlist.append(line)

            # Labels for major lines
            if round(y_px - origin_y) % 100 == 0:
                val = (origin_y - y_px) / 100
                label = QGraphicsSimpleTextItem(f"{val:.1f}")
                label.setBrush(QBrush(SCENE_COLORS["grid_label"]))
                label.setScale(0.8)
                br = label.boundingRect()
                label.setPos(-br.width() * 0.8 - 10, y_px - br.height() * 0.8 / 2)
                label.setZValue(-100)
                self.addItem(label)
                self.grid_drawlist.append(label)

    def set_grid_center(self, grid_center="Center"):
        if grid_center == "Center":
            self.origin_x = self.sheet_width / 2
            self.origin_y = self.sheet_height / 2

    def snap_to_grid(self, point: QPointF) -> QPointF:
        """Snaps a point to the nearest grid intersection (0.1 units = 10 pixels)."""
        grid_step = 10  # 0.1 units
        x = round(point.x() / grid_step) * grid_step
        y = round(point.y() / grid_step) * grid_step
        return QPointF(float(x), float(y))

    def update_selection_handles(self):
        """Update resize handles based on selection change."""

        for item in list(self.items()):
            if isinstance(item, ResizeHandle):
                self.removeItem(item)

        # Restore highlights for deselected items
        for item in list(self.selected_for_highlight):
            if not item.isSelected() or item.scene() != self:
                if hasattr(item, "_original_pen"):
                    item.setPen(item._original_pen)
                self.selected_for_highlight.remove(item)

        # Clear internal list
        self.selection_handles.clear()

        # Create handles for selected primitives
        for item in self.selectedItems():
            if item in self.symbol_drawlist:

                # Highlight
                if isinstance(item, (QGraphicsLineItem, QGraphicsRectItem, QGraphicsPolygonItem,
                                    QGraphicsPathItem, QGraphicsEllipseItem)):
                    if not hasattr(item, '_original_pen'):
                        item._original_pen = QPen(item.pen())
                    green_pen = QPen(SCENE_COLORS["highlight"])
                    green_pen.setWidth(item.pen().width())
                    green_pen.setStyle(item.pen().style())
                    item.setPen(green_pen)

                self.selected_for_highlight.add(item)
                self.create_handles_for_item(item)


    def create_handles_for_item(self, item):
        """Create resize handles for a specific item."""
        if isinstance(item, QGraphicsLineItem):
            line = item.line()
            self._add_handle(item, 0, item.mapToScene(line.p1()))
            self._add_handle(item, 1, item.mapToScene(line.p2()))
        elif isinstance(item, QGraphicsRectItem):
            r = item.rect()
            self._add_handle(item, 0, item.mapToScene(r.topLeft()))
            self._add_handle(item, 1, item.mapToScene(r.topRight()))
            self._add_handle(item, 2, item.mapToScene(r.bottomLeft()))
            self._add_handle(item, 3, item.mapToScene(r.bottomRight()))
        elif isinstance(item, QGraphicsPolygonItem):
            poly = item.polygon()
            for i in range(poly.count()):
                self._add_handle(item, i, item.mapToScene(poly[i]))
        elif isinstance(item, QGraphicsPathItem) and hasattr(item, "_points"):
            for i, pt in enumerate(item._points):
                self._add_handle(item, i, pt)

    def _add_handle(self, item, index, scene_pos):
        handle = ResizeHandle(item, index, self)
        handle.setPos(item.mapFromScene(scene_pos))
        self.selection_handles.append(handle)

    def update_item_geometry(self, item, index, scene_pos):
        """Update item geometry when a handle is moved."""
        local_pos = item.mapFromScene(scene_pos)
        if isinstance(item, QGraphicsLineItem):
            line = item.line()
            if index == 0:
                line.setP1(local_pos)
            else:
                line.setP2(local_pos)
            item.setLine(line)
        elif isinstance(item, QGraphicsRectItem):
            r = item.rect()
            if index == 0:
                r.setTopLeft(local_pos)
            elif index == 1:
                r.setTopRight(local_pos)
            elif index == 2:
                r.setBottomLeft(local_pos)
            elif index == 3:
                r.setBottomRight(local_pos)
            item.setRect(r.normalized())
        elif isinstance(item, QGraphicsPolygonItem):
            poly = item.polygon()
            if 0 <= index < poly.count():
                poly[index] = local_pos
                item.setPolygon(poly)
        elif isinstance(item, QGraphicsPathItem) and hasattr(item, "_points"):
            if 0 <= index < len(item._points):
                item._points[index] = scene_pos
                item.setPath(self._create_arc_path(item._points[0].x(), item._points[0].y(),
                                                   item._points[1].x(), item._points[1].y()))
        self.symbol_changed.emit()

    def keyPressEvent(self, event):
        if event is None:
            return
        if event.key() == Qt.Key.Key_Delete:
            to_remove = [item for item in self.selectedItems() if item in self.symbol_drawlist]
            if to_remove:
                indexed = sorted(
                    [(self.symbol_drawlist.index(item), item) for item in to_remove],
                    key=lambda x: x[0]
                )
                indices = [i for i, _ in indexed]
                to_remove = [item for _, item in indexed]
                for item in to_remove:
                    if item.scene() == self:
                        self.removeItem(item)
                    if item in self.symbol_drawlist:
                        self.symbol_drawlist.remove(item)
                    if item in self.selected_for_highlight:
                        self.selected_for_highlight.remove(item)
                self._push_undo_action("remove", to_remove, indices)
                self.update_selection_handles()
                self.symbol_changed.emit()
            return
        if event.key() == Qt.Key.Key_Z and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.undo()
        elif event.key() == Qt.Key.Key_Y and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.redo()
        elif event.key() == Qt.Key.Key_Escape:
            self.current_action = None
            self.clearSelection()
            QApplication.restoreOverrideCursor()
            for item in self.symbol_drawlist_temp:
                if item.scene() == self:
                    self.removeItem(item)
            self.symbol_drawlist_temp.clear()
            self.cursor_coordinates.clear()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Finish polyline on Enter
            if self.current_action in ["draw_polyline", "draw_polyline_orthogonal"]:
                if len(self.cursor_coordinates) >= 2:
                    if self.current_action == "draw_polyline":
                        self.draw_polyline(list(self.cursor_coordinates))
                    else:
                        self.draw_polyline_orthogonal(list(self.cursor_coordinates))

                    self.cursor_coordinates.clear()
                    self._clear_temp_preview()
                    self.current_action = None
                    while QApplication.overrideCursor() is not None:
                        QApplication.restoreOverrideCursor()

    def undo(self):
        if not self.undo_stack:
            return
        action = self.undo_stack.pop()
        action_type = action["type"]
        items = action["items"]
        indices = action.get("indices")
        before = action.get("before")

        if action_type == "add":
            for item in items:
                if item.scene() == self:
                    self.removeItem(item)
                if item in self.symbol_drawlist:
                    self.symbol_drawlist.remove(item)
        elif action_type == "remove":
            for i, item in enumerate(items):
                if item.scene() != self:
                    self.addItem(item)
                if item not in self.symbol_drawlist:
                    if indices and i < len(indices):
                        self.symbol_drawlist.insert(indices[i], item)
                    else:
                        self.symbol_drawlist.append(item)
        elif action_type == "transform" and before:
            for item, state in zip(items, before):
                self._apply_item_state(item, state)

        self.redo_stack.append(action)
        self.update_selection_handles()
        self.symbol_changed.emit()

    def redo(self):
        if not self.redo_stack:
            return
        action = self.redo_stack.pop()
        action_type = action["type"]
        items = action["items"]
        indices = action.get("indices")
        after = action.get("after")

        if action_type == "add":
            for i, item in enumerate(items):
                if item.scene() != self:
                    self.addItem(item)
                if item not in self.symbol_drawlist:
                    if indices and i < len(indices):
                        self.symbol_drawlist.insert(indices[i], item)
                    else:
                        self.symbol_drawlist.append(item)
        elif action_type == "remove":
            for item in items:
                if item.scene() == self:
                    self.removeItem(item)
                if item in self.symbol_drawlist:
                    self.symbol_drawlist.remove(item)
        elif action_type == "transform" and after:
            for item, state in zip(items, after):
                self._apply_item_state(item, state)

        self.undo_stack.append(action)
        self.update_selection_handles()
        self.symbol_changed.emit()

    def mousePressEvent(self, mouse_event):
        raw_pos = mouse_event.scenePos()
        self.cursor_position = self.snap_to_grid(raw_pos)
        btn = mouse_event.button()
        action = self.current_action

        # 1. Handle resize handle first
        item_at_click = self.itemAt(raw_pos, QTransform())
        if isinstance(item_at_click, ResizeHandle):
            super().mousePressEvent(mouse_event)
            return

        # 2. Left button logic
        if btn == Qt.MouseButton.LeftButton:

            # Move mode
            if action == "move_element":
                self._move_before_states = [
                    (item, self._capture_item_state(item))
                    for item in self.selectedItems()
                    if item in self.symbol_drawlist
                ]
                super().mousePressEvent(mouse_event)
                return

            # Selection mode
            if action == "select_element":
                super().mousePressEvent(mouse_event)
                return

            # Polyline handling (multi-point, finish on right-click)
            if action in ["draw_polyline", "draw_polyline_orthogonal"]:
                self.cursor_coordinates.append(self.cursor_position)
                return

            # Universal primitive handling
            if action in self.primitives:
                primitive = self.primitives[action]
                # Single-point primitives should finalize immediately
                if primitive.points_required == 1:
                    self.cursor_coordinates = [self.cursor_position]
                    self._finalize_primitive(primitive.draw_func)
                    return

                # Add point
                self.cursor_coordinates.append(self.cursor_position)

                # If enough points collected — draw
                if len(self.cursor_coordinates) == primitive.points_required:
                    self._finalize_primitive(primitive.draw_func)
                return

        # Right button - finish polyline
        if btn == Qt.MouseButton.RightButton:
            if action in ["draw_polyline", "draw_polyline_orthogonal"]:
                if len(self.cursor_coordinates) >= 2:
                    if action == "draw_polyline":
                        self.draw_polyline(list(self.cursor_coordinates))
                    else:
                        self.draw_polyline_orthogonal(list(self.cursor_coordinates))

                    # Reset state
                    self.cursor_coordinates.clear()
                    self._clear_temp_preview()
                    self.current_action = None
                    while QApplication.overrideCursor() is not None:
                        QApplication.restoreOverrideCursor()
                return

        # Fallback to default behavior
        super().mousePressEvent(mouse_event)

    def mouseReleaseEvent(self, mouse_event):
        super().mouseReleaseEvent(mouse_event)
        if self.current_action == "move_element" and self._move_before_states:
            items = [item for item, _ in self._move_before_states]
            before = [state for _, state in self._move_before_states]
            after = [self._capture_item_state(item) for item in items]
            if any(b != a for b, a in zip(before, after)):
                self._push_undo_action("transform", items, before=before, after=after)
                self.update_selection_handles()
                self.symbol_changed.emit()
            self._move_before_states = None

    def _finalize_primitive(self, draw_func):
        positions = list(self.cursor_coordinates)
        draw_func(positions)

        # Reset state
        self.cursor_coordinates.clear()
        self.current_action = None
        while QApplication.overrideCursor() is not None:
            QApplication.restoreOverrideCursor()

        # Remove temporary preview items
        for item in self.symbol_drawlist_temp:
            if item.scene() == self:
                self.removeItem(item)
        self.symbol_drawlist_temp.clear()

    def _preview_point(self, point_attr, point_class):
        """Preview a point while moving mouse"""
        if len(self.cursor_coordinates) == 0:
            self.cursor_coordinates.append(self.cursor_position)
        else:
            self.cursor_coordinates[0] = self.cursor_position

        point = getattr(self, point_attr)
        if point.scene() == self:
            self.removeItem(point)

        # Use connection type if applicable
        if point_class == SpindlePoint:
            new_point = point_class(self.last_selected_spindle)
        elif point_class in (ArrivePoint, LeavePoint, TeePoint):
            new_point = point_class(self.last_selected_connection_type)
        else:
            new_point = point_class()

        new_point.setPos(self.cursor_coordinates[0].x(), self.cursor_coordinates[0].y())
        setattr(self, point_attr, new_point)
        self.addItem(new_point)
        self.symbol_drawlist_temp.append(new_point)

    def _clear_temp_preview(self):
        for item in self.symbol_drawlist_temp:
            if item.scene() == self:
                self.removeItem(item)
        self.symbol_drawlist_temp.clear()

    def _preview_point_action(self, action):
        point_actions = {
            "draw_arrive_point": ("arrive_point", ArrivePoint),
            "draw_leave_point": ("leave_point", LeavePoint),
            "draw_tee_point": ("tee_point", TeePoint),
            "draw_spindle_point": ("spindle_point", SpindlePoint),
        }
        if action not in point_actions:
            return
        attr, cls = point_actions[action]
        self._preview_point(attr, cls)

    def _preview_two_point_primitive(self, action):
        if len(self.cursor_coordinates) == 0:
            return

        p0 = self.cursor_coordinates[0]
        p1 = self.cursor_position  # ВАЖНО: не трогаем cursor_coordinates

        self._clear_temp_preview()

        if action == "draw_line":
            item = QGraphicsLineItem(p0.x(), p0.y(), p1.x(), p1.y())



        elif action == "draw_rect":
            x1, y1 = p0.x(), p0.y()
            x2, y2 = p1.x(), p1.y()
            x, y = min(x1, x2), min(y1, y2)
            w, h = abs(x2 - x1), abs(y2 - y1)
            item = QGraphicsRectItem(x, y, w, h)

        elif action == "draw_square":
            x1, y1 = p0.x(), p0.y()
            x2, y2 = p1.x(), p1.y()
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            size = max(width, height)
            if x2 < x1:
                x = x1 - size
            else:
                x = x1
            if y2 < y1:
                y = y1 - size
            else:
                y = y1
            item = QGraphicsRectItem(x, y, size, size)

        elif action == "draw_circle":
            cx, cy = p0.x(), p0.y()
            dx, dy = p1.x() - cx, p1.y() - cy
            radius = (dx * dx + dy * dy) ** 0.5
            item = QGraphicsEllipseItem(cx - radius, cy - radius, radius * 2, radius * 2)

        elif action == "draw_diamond":
            cx, cy = p0.x(), p0.y()
            dx, dy = p1.x() - cx, p1.y() - cy
            radius = (dx * dx + dy * dy) ** 0.5
            polygon = QPolygonF()
            polygon.append(QPointF(cx, cy - radius))
            polygon.append(QPointF(cx + radius, cy))
            polygon.append(QPointF(cx, cy + radius))
            polygon.append(QPointF(cx - radius, cy))
            item = QGraphicsPolygonItem(polygon)

        elif action == "draw_cap":
            item = QGraphicsPathItem(self._create_arc_path(p0.x(), p0.y(), p1.x(), p1.y()))

        elif action == "draw_hexagon":
            cx, cy = p0.x(), p0.y()
            dx, dy = p1.x() - cx, p1.y() - cy
            radius = (dx * dx + dy * dy) ** 0.5
            item = QGraphicsPolygonItem(self._create_hexagon_polygon(cx, cy, radius))

        elif action == "draw_pentagon":
            cx, cy = p0.x(), p0.y()
            dx, dy = p1.x() - cx, p1.y() - cy
            radius = (dx * dx + dy * dy) ** 0.5
            item = QGraphicsPolygonItem(self._create_polygon(cx, cy, radius, 5))

        elif action == "draw_octagon":
            cx, cy = p0.x(), p0.y()
            dx, dy = p1.x() - cx, p1.y() - cy
            radius = (dx * dx + dy * dy) ** 0.5
            item = QGraphicsPolygonItem(self._create_polygon(cx, cy, radius, 8))

        elif action == "draw_dodecagon":
            cx, cy = p0.x(), p0.y()
            dx, dy = p1.x() - cx, p1.y() - cy
            radius = (dx * dx + dy * dy) ** 0.5
            item = QGraphicsPolygonItem(self._create_polygon(cx, cy, radius, 12))

        else:
            return  # Unknown action, don't create any preview

        item.setPen(self._create_pen())
        self.addItem(item)
        self.symbol_drawlist_temp.append(item)

    def _preview_triangle(self):
        if len(self.cursor_coordinates) == 0:
            return

        self._clear_temp_preview()

        # Build preview polygon from existing points + current cursor position
        polygon = QPolygonF()
        for point in self.cursor_coordinates:
            polygon.append(point)
        polygon.append(self.cursor_position)  # Add preview point without modifying cursor_coordinates

        self.triangle = QGraphicsPolygonItem(polygon)
        self.triangle.setPen(self._create_pen())
        self.addItem(self.triangle)
        self.symbol_drawlist_temp.append(self.triangle)

    def _preview_polyline(self, action):
        """Preview polyline as it's being drawn"""
        if len(self.cursor_coordinates) == 0:
            return

        self._clear_temp_preview()

        if action == "draw_polyline":
            # Regular polyline - connect points directly
            path = QPainterPath()
            path.moveTo(self.cursor_coordinates[0])
            for point in self.cursor_coordinates[1:]:
                path.lineTo(point)
            path.lineTo(self.cursor_position)  # Preview next segment

            preview = QGraphicsPathItem(path)
            preview.setPen(self._create_pen())
            self.addItem(preview)
            self.symbol_drawlist_temp.append(preview)

        elif action == "draw_polyline_orthogonal":
            # Orthogonal polyline - right angles only
            path = QPainterPath()
            path.moveTo(self.cursor_coordinates[0])

            # Draw existing segments
            for i in range(1, len(self.cursor_coordinates)):
                prev_pt = self.cursor_coordinates[i - 1]
                curr_pt = self.cursor_coordinates[i]

                dx = abs(curr_pt.x() - prev_pt.x())
                dy = abs(curr_pt.y() - prev_pt.y())

                if dx >= dy:
                    path.lineTo(curr_pt.x(), prev_pt.y())
                    path.lineTo(curr_pt.x(), curr_pt.y())
                else:
                    path.lineTo(prev_pt.x(), curr_pt.y())
                    path.lineTo(curr_pt.x(), curr_pt.y())

            # Preview next segment
            if len(self.cursor_coordinates) > 0:
                last_pt = self.cursor_coordinates[-1]
                dx = abs(self.cursor_position.x() - last_pt.x())
                dy = abs(self.cursor_position.y() - last_pt.y())

                if dx >= dy:
                    path.lineTo(self.cursor_position.x(), last_pt.y())
                    path.lineTo(self.cursor_position.x(), self.cursor_position.y())
                else:
                    path.lineTo(last_pt.x(), self.cursor_position.y())
                    path.lineTo(self.cursor_position.x(), self.cursor_position.y())

            preview = QGraphicsPathItem(path)
            preview.setPen(self._create_pen())
            self.addItem(preview)
            self.symbol_drawlist_temp.append(preview)

    def mouseMoveEvent(self, mouse_event):
        self.cursor_position = self.snap_to_grid(mouse_event.scenePos())
        action = self.current_action

        # Preview polyline
        if action in ["draw_polyline", "draw_polyline_orthogonal"]:
            self._preview_polyline(action)
            return

        if action not in self.primitives:
            super().mouseMoveEvent(mouse_event)
            return

        primitive = self.primitives[action]
        points_needed = primitive.points_required

        if points_needed == 1:
            self._preview_point_action(action)
            return

        if points_needed == 2:
            self._preview_two_point_primitive(action)
            return

        if points_needed == 3:
            self._preview_triangle()
            return

        super().mouseMoveEvent(mouse_event)

    def _finalize_item(self, item):
        """Common finalization for drawn items"""
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.addItem(item)
        self.symbol_drawlist.append(item)
        self.cursor_coordinates.clear()
        while QApplication.overrideCursor() is not None:
            QApplication.restoreOverrideCursor()
        self._push_undo_action("add", [item])
        self.symbol_changed.emit()

    def _create_pen(self):
        """Create standard pen for drawing"""
        pen = QPen(SCENE_COLORS["default_pen"])
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.SolidLine)
        return pen

    def _draw_point(self, point_class):
        """Generic point drawing method"""
        if point_class == SpindlePoint:
            point = point_class(self.last_selected_spindle)
        elif point_class in (ArrivePoint, LeavePoint, TeePoint):
            point = point_class(self.last_selected_connection_type)
        else:
            point = point_class()

        pos = self.cursor_coordinates[0]
        point.setPos(pos.x(), pos.y())
        self._finalize_item(point)

    def clear_symbol_drawlist(self):
        """Clear all symbols from the drawing list and scene"""
        for item in self.symbol_drawlist:
            if item.scene() == self:
                self.removeItem(item)
        self.symbol_drawlist.clear()
        self.symbol_changed.emit()

    def _push_undo_action(self, action_type, items, indices=None, **kwargs):
        action = {
            "type": action_type,
            "items": list(items),
            "indices": list(indices) if indices is not None else None,
        }
        action.update(kwargs)
        self.undo_stack.append(action)
        self.redo_stack.clear()

    def _capture_item_state(self, item):
        if isinstance(item, QGraphicsLineItem):
            line = item.line()
            geom = (line.x1(), line.y1(), line.x2(), line.y2())
        elif isinstance(item, QGraphicsRectItem):
            rect = item.rect()
            geom = (rect.x(), rect.y(), rect.width(), rect.height())
        elif isinstance(item, QGraphicsPolygonItem):
            poly = item.polygon()
            geom = [(poly[i].x(), poly[i].y()) for i in range(poly.count())]
        elif isinstance(item, QGraphicsPathItem) and hasattr(item, "_points"):
            geom = [(p.x(), p.y()) for p in item._points]
        else:
            return None
        return {
            "pos": (item.pos().x(), item.pos().y()),
            "geom": geom,
        }

    def _apply_item_state(self, item, state):
        if state is None:
            return
        pos_x, pos_y = state["pos"]
        item.setPos(QPointF(pos_x, pos_y))
        geom = state["geom"]
        if isinstance(item, QGraphicsLineItem):
            item.setLine(geom[0], geom[1], geom[2], geom[3])
        elif isinstance(item, QGraphicsRectItem):
            item.setRect(geom[0], geom[1], geom[2], geom[3])
        elif isinstance(item, QGraphicsPolygonItem):
            polygon = QPolygonF()
            for x, y in geom:
                polygon.append(QPointF(x, y))
            item.setPolygon(polygon)
        elif isinstance(item, QGraphicsPathItem) and hasattr(item, "_points"):
            item._points = [QPointF(x, y) for x, y in geom]
            if len(item._points) >= 2:
                item.setPath(self._create_arc_path(item._points[0].x(), item._points[0].y(),
                                                   item._points[1].x(), item._points[1].y()))

    def select_all_items(self):
        """Select all items in the symbol_drawlist"""
        if not hasattr(self, 'selected_for_highlight'):
            self.selected_for_highlight = set()

        for item in self.symbol_drawlist:
            item.setSelected(True)
            self.selected_for_highlight.add(item)

            if isinstance(item, (QGraphicsLineItem, QGraphicsRectItem, QGraphicsPolygonItem,
                                 QGraphicsPathItem, QGraphicsEllipseItem)):
                if not hasattr(item, '_original_pen'):
                    item._original_pen = QPen(item.pen())
                green_pen = QPen(SCENE_COLORS["highlight"])
                green_pen.setWidth(item.pen().width())
                green_pen.setStyle(item.pen().style())
                item.setPen(green_pen)

    def draw_arrive_point(self, _positions):
        self._draw_point(ArrivePoint)

    def draw_leave_point(self, _positions):
        self._draw_point(LeavePoint)

    def draw_tee_point(self, _positions):
        self._draw_point(TeePoint)

    def draw_spindle_point(self, _positions):
        point = SpindlePoint(self.last_selected_spindle)
        pos = self.cursor_coordinates[0]
        point.setPos(pos.x(), pos.y())
        self._finalize_item(point)
        self.spindle_point_placed.emit(self.last_selected_spindle, pos)

    def draw_line(self, positions):
        p0, p1 = positions[0], positions[1]
        line = QGraphicsLineItem(p0.x(), p0.y(), p1.x(), p1.y())
        line.setPen(self._create_pen())
        self._finalize_item(line)

    def draw_polyline(self, positions):
        """Draw a polyline from multiple points"""
        if len(positions) < 2:
            return

        path = QPainterPath()
        path.moveTo(positions[0])
        for point in positions[1:]:
            path.lineTo(point)

        polyline = QGraphicsPathItem(path)
        polyline.setPen(self._create_pen())
        self._finalize_item(polyline)

    def draw_polyline_orthogonal(self, positions):
        """Draw an orthogonal (right-angle) polyline from multiple points"""
        if len(positions) < 2:
            return

        path = QPainterPath()
        path.moveTo(positions[0])

        for i in range(1, len(positions)):
            prev_pt = positions[i - 1]
            curr_pt = positions[i]

            # Calculate whether to go horizontal or vertical first
            dx = abs(curr_pt.x() - prev_pt.x())
            dy = abs(curr_pt.y() - prev_pt.y())

            # Go in the direction of larger change first
            if dx >= dy:
                # Horizontal then vertical
                path.lineTo(curr_pt.x(), prev_pt.y())
                path.lineTo(curr_pt.x(), curr_pt.y())
            else:
                # Vertical then horizontal
                path.lineTo(prev_pt.x(), curr_pt.y())
                path.lineTo(curr_pt.x(), curr_pt.y())

        polyline = QGraphicsPathItem(path)
        polyline.setPen(self._create_pen())
        self._finalize_item(polyline)

    def draw_rect(self, positions):
        p0, p1 = positions[0], positions[1]
        x1, y1 = p0.x(), p0.y()
        x2, y2 = p1.x(), p1.y()
        x, y = min(x1, x2), min(y1, y2)
        w, h = abs(x2 - x1), abs(y2 - y1)

        rect = QGraphicsRectItem(x, y, w, h)
        rect.setPen(self._create_pen())
        self._finalize_item(rect)

    def draw_triangle(self, positions):
        polygon = QPolygonF()
        for point in positions:
            polygon.append(point)

        triangle = QGraphicsPolygonItem(polygon)
        triangle.setPen(self._create_pen())
        self._finalize_item(triangle)

    def _create_arc_path(self, x1, y1, x2, y2):
        """Create arc path between two points"""
        path = QPainterPath()
        path.moveTo(x1, y1)
        dx, dy = x2 - x1, y2 - y1
        length = (dx * dx + dy * dy) ** 0.5
        if length > 0:
            nx, ny = -dy / length, dx / length
        else:
            nx, ny = 0, 1
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        arc_height = length / 2
        path.quadTo(mid_x + nx * arc_height, mid_y + ny * arc_height, x2, y2)
        return path

    def draw_cap(self, positions):
        p0, p1 = positions[0], positions[1]
        x1, y1 = p0.x(), p0.y()
        x2, y2 = p1.x(), p1.y()

        cap = QGraphicsPathItem(self._create_arc_path(x1, y1, x2, y2))
        cap._points = [QPointF(x1, y1), QPointF(x2, y2)]
        cap.setPen(self._create_pen())
        self._finalize_item(cap)

    def _create_hexagon_polygon(self, cx, cy, radius):
        """Create hexagon polygon from center and radius"""
        polygon = QPolygonF()
        for i in range(6):
            angle = math.pi / 3 * i - math.pi / 2  # Start from top
            polygon.append(QPointF(cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
        return polygon

    def draw_hexagon(self, positions):
        p0, p1 = positions[0], positions[1]
        cx, cy = p0.x(), p0.y()
        dx, dy = p1.x() - cx, p1.y() - cy
        radius = (dx * dx + dy * dy) ** 0.5

        hexagon = QGraphicsPolygonItem(self._create_hexagon_polygon(cx, cy, radius))
        hexagon.setPen(self._create_pen())
        self._finalize_item(hexagon)

    def _create_polygon(self, cx, cy, radius, sides):
        """Create regular polygon from center, radius and number of sides"""
        polygon = QPolygonF()
        for i in range(sides):
            angle = 2 * math.pi / sides * i - math.pi / 2  # Start from top
            polygon.append(QPointF(cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
        return polygon

    def draw_square(self, positions):
        """Draw a square with equal width and height"""
        p0, p1 = positions[0], positions[1]
        x1, y1 = p0.x(), p0.y()
        x2, y2 = p1.x(), p1.y()

        # Calculate size based on maximum dimension
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        size = max(width, height)

        # Determine position maintaining direction
        if x2 < x1:
            x = x1 - size
        else:
            x = x1
        if y2 < y1:
            y = y1 - size
        else:
            y = y1

        square = QGraphicsRectItem(x, y, size, size)
        square.setPen(self._create_pen())
        self._finalize_item(square)

    def draw_circle(self, positions):
        """Draw a circle from center and radius point"""
        p0, p1 = positions[0], positions[1]
        cx, cy = p0.x(), p0.y()
        dx, dy = p1.x() - cx, p1.y() - cy
        radius = (dx * dx + dy * dy) ** 0.5

        circle = QGraphicsEllipseItem(cx - radius, cy - radius, radius * 2, radius * 2)
        circle.setPen(self._create_pen())
        self._finalize_item(circle)

    def draw_diamond(self, positions):
        """Draw a diamond (square rotated 45 degrees)"""
        p0, p1 = positions[0], positions[1]
        cx, cy = p0.x(), p0.y()
        dx, dy = p1.x() - cx, p1.y() - cy
        radius = (dx * dx + dy * dy) ** 0.5

        # Create diamond with 4 points at cardinal directions
        polygon = QPolygonF()
        polygon.append(QPointF(cx, cy - radius))  # Top
        polygon.append(QPointF(cx + radius, cy))  # Right
        polygon.append(QPointF(cx, cy + radius))  # Bottom
        polygon.append(QPointF(cx - radius, cy))  # Left

        diamond = QGraphicsPolygonItem(polygon)
        diamond.setPen(self._create_pen())
        self._finalize_item(diamond)

    def draw_pentagon(self, positions):
        """Draw a regular pentagon"""
        p0, p1 = positions[0], positions[1]
        cx, cy = p0.x(), p0.y()
        dx, dy = p1.x() - cx, p1.y() - cy
        radius = (dx * dx + dy * dy) ** 0.5

        pentagon = QGraphicsPolygonItem(self._create_polygon(cx, cy, radius, 5))
        pentagon.setPen(self._create_pen())
        self._finalize_item(pentagon)

    def draw_octagon(self, positions):
        """Draw a regular octagon"""
        p0, p1 = positions[0], positions[1]
        cx, cy = p0.x(), p0.y()
        dx, dy = p1.x() - cx, p1.y() - cy
        radius = (dx * dx + dy * dy) ** 0.5

        octagon = QGraphicsPolygonItem(self._create_polygon(cx, cy, radius, 8))
        octagon.setPen(self._create_pen())
        self._finalize_item(octagon)

    def draw_dodecagon(self, positions):
        """Draw a regular dodecagon (12-sided polygon)"""
        p0, p1 = positions[0], positions[1]
        cx, cy = p0.x(), p0.y()
        dx, dy = p1.x() - cx, p1.y() - cy
        radius = (dx * dx + dy * dy) ** 0.5

        dodecagon = QGraphicsPolygonItem(self._create_polygon(cx, cy, radius, 12))
        dodecagon.setPen(self._create_pen())
        self._finalize_item(dodecagon)