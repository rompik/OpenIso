# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import math
from collections import namedtuple
from PyQt6.QtWidgets import (
    QGraphicsScene, QGraphicsLineItem, QGraphicsRectItem, QGraphicsEllipseItem,
    QGraphicsPolygonItem, QGraphicsSimpleTextItem, QGraphicsItem, QApplication,
    QGraphicsPathItem
)
from PyQt6.QtGui import (
    QPolygonF, QColor, QPen, QPainterPath, QTransform, QBrush
)
from PyQt6.QtCore import Qt, QPointF, pyqtSignal, QRectF
from openiso.view.geometry_items import ArrivePoint, LeavePoint, TeePoint, SpindlePoint


class ResizeHandle(QGraphicsRectItem):
    """A small marker at the edges of a primitive to resize it."""
    def __init__(self, parent_item, index, scene):
        super().__init__(QRectF(-4, -4, 8, 8), parent_item)
        self.parent_item = parent_item
        self.index = index
        self.scene_ref = scene
        self.setBrush(QBrush(QColor(255, 255, 255)))
        self.setPen(QPen(QColor(0, 0, 0), 1))
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


class SheetLayout(QGraphicsScene):
    spindle_point_placed = pyqtSignal(str, QPointF)

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
        from openiso.core.constants import SHEET_SIZE
        self.sheet_width = SHEET_SIZE
        self.sheet_height = SHEET_SIZE
        self.step_x = 5
        self.step_y = 5
        self.origin_x = 0
        self.origin_y = 0

        self.current_action = ""
        self.press_number = 0
        self.cursor_position = QPointF(0.0, 0.0)
        self.point_diameter = 5

        self.draw_grid()
        self.selectionChanged.connect(self.update_selection_handles)

        Primitive = namedtuple("Primitive", ["points_required", "draw_func"])

        self.primitives = {
            "draw_line": Primitive(2, self.draw_line),
            "draw_rect": Primitive(2, self.draw_rect),
            "draw_triangle": Primitive(3, self.draw_triangle),
            "draw_cap": Primitive(2, self.draw_cap),
            "draw_hexagon": Primitive(2, self.draw_hexagon),
            "draw_arrive_point": Primitive(1, self.draw_arrive_point),
            "draw_leave_point": Primitive(1, self.draw_leave_point),
            "draw_tee_point": Primitive(1, self.draw_tee_point),
            "draw_spindle_point": Primitive(1, self.draw_spindle_point),
        }


    def convert_to_relative_position(self, scene_position):
        # Use SHEET_SIZE for fixed coordinate system
        from openiso.core.constants import SHEET_SIZE
        x = (scene_position.x() - SHEET_SIZE / 2) / (self.step_x * 20)
        y = (SHEET_SIZE / 2 - scene_position.y()) / (self.step_y * 20)
        return QPointF(round(x, 3), round(y, 3))

    def draw_grid(self):
        """Draws a hierarchical grid that is fixed at SHEET_SIZE."""
        from openiso.core.constants import SHEET_SIZE
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
        pen_origin = QPen(QColor(100, 100, 100), 1.2, Qt.PenStyle.SolidLine)
        pen_major = QPen(QColor(180, 180, 180), 0.8, Qt.PenStyle.SolidLine)  # 1.0 units (100px)
        pen_middle = QPen(QColor(210, 210, 210), 0.5, Qt.PenStyle.DashLine)  # 0.5 units (50px)
        pen_minor = QPen(QColor(230, 230, 230), 0.3, Qt.PenStyle.SolidLine)  # 0.1 units (10px)

        # Draw Vertical Lines
        for x_px in range(0, int(width) + 1, 10):
            if abs(x_px - origin_x) < 1: # Float comparison for center
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
                label.setBrush(QBrush(QColor(100, 100, 100)))
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
                label.setBrush(QBrush(QColor(100, 100, 100)))
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
        # Restore highlights for deselected items
        for item in list(self.selected_for_highlight):
            if not item.isSelected() or item.scene() != self:
                if hasattr(item, "_original_pen"):
                    item.setPen(item._original_pen)
                # We no longer restore brush here as we don't change it anymore
                self.selected_for_highlight.remove(item)

        # Clear existing handles
        for handle in self.selection_handles:
            if handle.scene() == self:
                self.removeItem(handle)
        self.selection_handles.clear()

        # Create handles for selected primitives and apply highlight (pen only)
        for item in self.selectedItems():
            if item in self.symbol_drawlist:
                # Save original pen and set green color
                if isinstance(item, (QGraphicsLineItem, QGraphicsRectItem, QGraphicsPolygonItem,
                                    QGraphicsPathItem, QGraphicsEllipseItem)):
                    if not hasattr(item, '_original_pen'):
                        item._original_pen = QPen(item.pen())
                    green_pen = QPen(QColor(0, 200, 0))
                    green_pen.setWidth(item.pen().width())
                    green_pen.setStyle(item.pen().style())
                    item.setPen(green_pen)

                # We no longer change the brush (fill color) here

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

    def keyPressEvent(self, event):
        if event is None:
            return
        if event.key() == Qt.Key.Key_Z and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.undo()
        elif event.key() == Qt.Key.Key_Y and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.redo()
        elif event.key() == Qt.Key.Key_Escape:
            self.press_number = 0
            self.current_action = ""
            self.clearSelection()
            QApplication.restoreOverrideCursor()
            for item in self.symbol_drawlist_temp:
                if item.scene() == self:
                    self.removeItem(item)
            self.symbol_drawlist_temp.clear()

    def undo(self):
        print("Delete the last line from self.drawlist and draw all the others")

    def redo(self):
        print("Delete the last line from self.drawlist and draw all the others")

    def mousePressEvent(self, mouse_event):
        raw_pos = mouse_event.scenePos()
        self.cursor_position = self.snap_to_grid(raw_pos)
        btn = mouse_event.button()
        action = self.current_action

        # 1. Проверка на handle
        item_at_click = self.itemAt(raw_pos, QTransform())
        if isinstance(item_at_click, ResizeHandle):
            super().mousePressEvent(mouse_event)
            return

        # 2. ЛКМ
        if btn == Qt.MouseButton.LeftButton:

            # Режим выделения
            if action == "select_element":
                super().mousePressEvent(mouse_event)
                return

            # 3. Универсальная обработка примитивов
            if action in self.primitives:
                primitive = self.primitives[action]

                # Добавляем точку
                self.cursor_coordinates.append(self.cursor_position)

                # Если точек достаточно — рисуем
                if len(self.cursor_coordinates) == primitive.points_required:
                    self._finalize_primitive(primitive.draw_func)
                return

        # Если ничего не подошло — отдаём событие дальше
        super().mousePressEvent(mouse_event)

    def _finalize_primitive(self, draw_func):
        draw_func(self.cursor_coordinates)

        # Сброс состояния
        self.cursor_coordinates.clear()
        self.current_action = None
        QApplication.restoreOverrideCursor()

        # Удаляем временные элементы
        for item in self.symbol_drawlist_temp:
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

    def mouseMoveEvent(self, mouse_event):
        self.cursor_position = self.snap_to_grid(mouse_event.scenePos())

        # Point preview handling
        point_actions = {
            "draw_arrive_point": ("arrive_point", ArrivePoint),
            "draw_leave_point": ("leave_point", LeavePoint),
            "draw_tee_point": ("tee_point", TeePoint),
            "draw_spindle_point": ("spindle_point", SpindlePoint),
        }

        if self.press_number == 0 and self.current_action in point_actions:
            attr, cls = point_actions[self.current_action]
            self._preview_point(attr, cls)
            return

        if self.press_number == 1 and self.current_action == "draw_line":
            if len(self.cursor_coordinates) == 1:
                self.cursor_coordinates.append(self.cursor_position)
                self.line = QGraphicsLineItem(self.cursor_coordinates[0].x(), self.cursor_coordinates[0].y(),
                                               self.cursor_coordinates[1].x(), self.cursor_coordinates[1].y())
                self.addItem(self.line)
                self.symbol_drawlist_temp.append(self.line)

            elif len(self.cursor_coordinates) == 2:
                self.cursor_coordinates[1] = self.cursor_position
                if self.line.scene() == self:
                    self.removeItem(self.line)
                self.line = QGraphicsLineItem(self.cursor_coordinates[0].x(), self.cursor_coordinates[0].y(),
                                               self.cursor_coordinates[1].x(), self.cursor_coordinates[1].y())
                self.addItem(self.line)
                self.symbol_drawlist_temp.append(self.line)

        elif self.press_number == 1 and self.current_action == "draw_rect":
            if len(self.cursor_coordinates) == 1:
                self.cursor_coordinates.append(self.cursor_position)

            elif len(self.cursor_coordinates) == 2:
                self.cursor_coordinates[1] = self.cursor_position
                if self.rect.scene() == self:
                    self.removeItem(self.rect)

            if self.cursor_coordinates[0].x() <= self.cursor_coordinates[1].x():
                pos_x_left = self.cursor_coordinates[0].x()
                pos_x_right = self.cursor_coordinates[1].x()
            else:
                pos_x_left = self.cursor_coordinates[1].x()
                pos_x_right = self.cursor_coordinates[0].x()

            if self.cursor_coordinates[0].y() <= self.cursor_coordinates[1].y():
                pos_y_bottom = self.cursor_coordinates[1].y()
                pos_y_top = self.cursor_coordinates[0].y()
            else:
                pos_y_bottom = self.cursor_coordinates[0].y()
                pos_y_top = self.cursor_coordinates[1].y()

            rect_width = abs(pos_x_right - pos_x_left)
            rect_height = abs(pos_y_bottom - pos_y_top)

            self.rect = QGraphicsRectItem(pos_x_left, pos_y_top, rect_width, rect_height)
            self.addItem(self.rect)
            self.symbol_drawlist_temp.append(self.rect)

        elif self.press_number == 1 and self.current_action == "draw_triangle":
            if self.press_number == 1 and len(self.cursor_coordinates) == 1:
                self.cursor_coordinates.append(self.cursor_position)
            elif self.press_number == 1 and len(self.cursor_coordinates) == 2:
                self.cursor_coordinates[self.press_number] = self.cursor_position

            if self.triangle.scene() == self:
                self.removeItem(self.triangle)
            polygon = QPolygonF()
            for point in self.cursor_coordinates:
                polygon.append(point)

            self.triangle = QGraphicsPolygonItem(polygon)
            self.addItem(self.triangle)
            self.symbol_drawlist_temp.append(self.triangle)

        elif self.press_number == 2 and self.current_action == "draw_triangle":
            if self.press_number == 2 and len(self.cursor_coordinates) == 2:
                self.cursor_coordinates.append(self.cursor_position)
            elif self.press_number == 2 and len(self.cursor_coordinates) == 3:
                self.cursor_coordinates[self.press_number] = self.cursor_position

            if self.triangle.scene() == self:
                self.removeItem(self.triangle)
            polygon = QPolygonF()
            for point in self.cursor_coordinates:
                polygon.append(point)

            self.triangle = QGraphicsPolygonItem(polygon)
            self.addItem(self.triangle)
            self.symbol_drawlist_temp.append(self.triangle)

        elif self.press_number == 1 and self.current_action == "draw_cap":
            if len(self.cursor_coordinates) == 1:
                self.cursor_coordinates.append(self.cursor_position)
            elif len(self.cursor_coordinates) == 2:
                self.cursor_coordinates[1] = self.cursor_position
                if self.cap.scene() == self:
                    self.removeItem(self.cap)

            x1, y1 = self.cursor_coordinates[0].x(), self.cursor_coordinates[0].y()
            x2, y2 = self.cursor_coordinates[1].x(), self.cursor_coordinates[1].y()
            self.cap = QGraphicsPathItem(self._create_arc_path(x1, y1, x2, y2))
            self.addItem(self.cap)
            self.symbol_drawlist_temp.append(self.cap)

        elif self.press_number == 1 and self.current_action == "draw_hexagon":
            if len(self.cursor_coordinates) == 1:
                self.cursor_coordinates.append(self.cursor_position)
            elif len(self.cursor_coordinates) == 2:
                self.cursor_coordinates[1] = self.cursor_position
                if self.hexagon.scene() == self:
                    self.removeItem(self.hexagon)

            cx, cy = self.cursor_coordinates[0].x(), self.cursor_coordinates[0].y()
            dx, dy = self.cursor_coordinates[1].x() - cx, self.cursor_coordinates[1].y() - cy
            radius = (dx * dx + dy * dy) ** 0.5

            self.hexagon = QGraphicsPolygonItem(self._create_hexagon_polygon(cx, cy, radius))
            self.addItem(self.hexagon)
            self.symbol_drawlist_temp.append(self.hexagon)

    def _finalize_item(self, item):
        """Common finalization for drawn items"""
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.addItem(item)
        self.symbol_drawlist.append(item)
        self.cursor_coordinates.clear()
        while QApplication.overrideCursor() is not None:
            QApplication.restoreOverrideCursor()

    def _create_pen(self):
        """Create standard pen for drawing"""
        pen = QPen(QColor(0, 0, 0))
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

        point.setPos(self.cursor_coordinates[0].x(), self.cursor_coordinates[0].y())
        self._finalize_item(point)

    def clear_symbol_drawlist(self):
        """Clear all symbols from the drawing list and scene"""
        for item in self.symbol_drawlist:
            if item.scene() == self:
                self.removeItem(item)
        self.symbol_drawlist.clear()

    def select_all_items(self):
        """Select all items in the symbol_drawlist"""
        if not hasattr(self, 'selected_for_highlight'):
            self.selected_for_highlight = set()

        for item in self.symbol_drawlist:
            item.setSelected(True)
            self.selected_for_highlight.add(item)

            # Highlight (pen only, as requested)
            if isinstance(item, (QGraphicsLineItem, QGraphicsRectItem, QGraphicsPolygonItem,
                                QGraphicsPathItem, QGraphicsEllipseItem)):
                if not hasattr(item, '_original_pen'):
                    item._original_pen = QPen(item.pen())
                green_pen = QPen(QColor(0, 200, 0))
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
        # Notify that a spindle point was placed to load geometry
        self.spindle_point_placed.emit(self.last_selected_spindle, pos)

    def draw_line(self, _positions):
        line = QGraphicsLineItem(
            self.cursor_coordinates[0].x(), self.cursor_coordinates[0].y(),
            self.cursor_coordinates[1].x(), self.cursor_coordinates[1].y()
        )
        line.setPen(self._create_pen())
        self._finalize_item(line)

    def draw_rect(self, _positions):
        x1, y1 = self.cursor_coordinates[0].x(), self.cursor_coordinates[0].y()
        x2, y2 = self.cursor_coordinates[1].x(), self.cursor_coordinates[1].y()
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

    def draw_cap(self, _positions):
        x1, y1 = self.cursor_coordinates[0].x(), self.cursor_coordinates[0].y()
        x2, y2 = self.cursor_coordinates[1].x(), self.cursor_coordinates[1].y()

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

    def draw_hexagon(self, _positions):
        cx, cy = self.cursor_coordinates[0].x(), self.cursor_coordinates[0].y()
        dx, dy = self.cursor_coordinates[1].x() - cx, self.cursor_coordinates[1].y() - cy
        radius = (dx * dx + dy * dy) ** 0.5

        hexagon = QGraphicsPolygonItem(self._create_hexagon_polygon(cx, cy, radius))
        hexagon.setPen(self._create_pen())
        self._finalize_item(hexagon)
