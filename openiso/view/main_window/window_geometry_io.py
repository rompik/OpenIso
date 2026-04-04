#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""Geometry I/O mixin for SkeyEditor."""

from __future__ import annotations

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QBrush, QColor, QPen, QPolygonF
from PyQt6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsPolygonItem,
    QGraphicsRectItem,
)

from openiso.view.graphics.geometry_items import (
    ArrivePoint,
    LeavePoint,
    SpindlePoint,
    TeePoint,
)


class GeometryIOMixin:
    """Mixin providing geometry loading, serialisation and coordinate helpers for SkeyEditor."""

    # -----------------------------------------------------------------
    # Spindle geometry
    # -----------------------------------------------------------------

    def _on_spindle_selected(self, spindle_skey_name):
        """Adds spindle geometry to the scene at the location of an existing SpindlePoint."""
        if not spindle_skey_name:
            return

        spindle_points = [
            item for item in self.scene.items()
            if isinstance(item, SpindlePoint)
        ]
        if not spindle_points:
            return

        geometry_list = self.skey_service.get_spindle_geometry(spindle_skey_name)
        if not geometry_list:
            print(f"No geometry found for spindle: {spindle_skey_name}")
            return

        for point in spindle_points:
            if point.spindle_name != spindle_skey_name:
                continue
            pos = point.pos()
            self._load_spindle_geometry_to_scene(geometry_list, pos.x(), pos.y())

    def _on_spindle_point_placed(self, spindle_name, pos):
        """Loads and positions spindle geometry onto the scene when a SpindlePoint is placed."""
        if not spindle_name:
            return

        print(f"Loading spindle geometry for '{spindle_name}' at {pos.x()}, {pos.y()}")
        geometry_list = self.skey_service.get_spindle_geometry(spindle_name)
        if not geometry_list:
            print(f"No geometry found for spindle: {spindle_name}")
            return

        self._load_spindle_geometry_to_scene(geometry_list, pos.x(), pos.y())
        self.preview_widget.update_preview(self.scene.symbol_drawlist, self.origin_x, self.origin_y)

    def _load_spindle_geometry_to_scene(self, geometry, base_x, base_y):
        """Loads and positions spindle geometry onto the scene based on a reference point."""
        for item_str in geometry:
            try:
                item_type = item_str.split(":")[0].strip()
                if item_type not in ("Line", "Rectangle", "Polygon", "Circle"):
                    continue

                parts = item_str.split(":")
                if len(parts) < 2:
                    continue
                values = self._parse_key_value_params(parts[1].strip())

                if item_type == "Line":
                    x1 = values.get("x1", 0) * self.scene.step_x * 20 + base_x
                    y1 = base_y - values.get("y1", 0) * self.scene.step_y * 20
                    x2 = values.get("x2", 0) * self.scene.step_x * 20 + base_x
                    y2 = base_y - values.get("y2", 0) * self.scene.step_y * 20
                    line = QGraphicsLineItem(x1, y1, x2, y2)
                    line.setPen(QPen(QColor(0, 0, 0), 2))
                    self._add_graphics_element(line)

                elif item_type == "Rectangle":
                    x0 = values.get("x0", 0) * self.scene.step_x * 20 + base_x
                    y0 = base_y - values.get("y0", 0) * self.scene.step_y * 20
                    w = values.get("width", 0) * self.scene.step_x * 20
                    h = values.get("height", 0) * self.scene.step_y * 20
                    rect = QGraphicsRectItem(x0 - w / 2, y0 - h / 2, w, h)
                    rect.setPen(QPen(QColor(0, 0, 0), 2))
                    self._add_graphics_element(rect)

                elif item_type == "Polygon":
                    polygon = QPolygonF()
                    i = 1
                    while f"p{i}x" in values and f"p{i}y" in values:
                        px = values[f"p{i}x"] * self.scene.step_x * 20 + base_x
                        py = base_y - values[f"p{i}y"] * self.scene.step_y * 20
                        polygon.append(QPointF(px, py))
                        i += 1
                    if not polygon.isEmpty():
                        poly_item = QGraphicsPolygonItem(polygon)
                        poly_item.setPen(QPen(QColor(0, 0, 0), 2))
                        poly_item.setBrush(QBrush(QColor(150, 150, 150, 100)))
                        self._add_graphics_element(poly_item)

                elif item_type == "Circle":
                    x0 = values.get("x0", 0) * self.scene.step_x * 20 + base_x
                    y0 = base_y - values.get("y0", 0) * self.scene.step_y * 20
                    r = values.get("r", 0) * self.scene.step_x * 20
                    circle = QGraphicsEllipseItem(x0 - r, y0 - r, 2 * r, 2 * r)
                    circle.setPen(QPen(QColor(0, 0, 0), 2))
                    self._add_graphics_element(circle)

            except Exception as e:
                print(f"Error drawing spindle item {item_str}: {e}")

    # -----------------------------------------------------------------
    # Scene geometry loading
    # -----------------------------------------------------------------

    def _add_graphics_element(self, element):
        """Helper method to add a new graphics item to the scene and tracking list."""
        element.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.scene.addItem(element)
        self.scene.symbol_drawlist.append(element)

    def _load_geometry_to_scene(self, geometry):
        """Parses geometry data strings and renders the corresponding items on the canvas."""
        point_types = {
            "ArrivePoint": ArrivePoint,
            "LeavePoint": LeavePoint,
            "TeePoint": TeePoint,
            "SpindlePoint": SpindlePoint,
        }

        for item_str in geometry:
            try:
                item_type = item_str.split(":")[0].strip()

                if item_type in point_types:
                    parts = item_str.split(":")
                    if len(parts) < 2:
                        continue
                    params = parts[1].strip()
                    values: dict = {}
                    for param in params.split():
                        if "=" in param:
                            key, val = param.split("=")
                            if key in ("x0", "y0"):
                                values[key] = float(val)
                            else:
                                values[key] = val

                    x0_rel = values.get("x0", 0)
                    y0_rel = values.get("y0", 0)
                    x0 = x0_rel * self.scene.step_x * 20 + self.scene.sheet_width / 2
                    y0 = self.scene.sheet_height / 2 - y0_rel * self.scene.step_y * 20

                    point_class = point_types[item_type]
                    if point_class == SpindlePoint:
                        spindle_name = values.get("name", "")
                        element = point_class(
                            spindle_name=spindle_name,
                            point_type=values.get("type", ""),
                        )
                        if spindle_name:
                            geometry_list = self.skey_service.get_spindle_geometry(spindle_name)
                            if geometry_list:
                                self._load_spindle_geometry_to_scene(geometry_list, x0, y0)
                    else:
                        element = point_class(point_type=values.get("type", ""))

                    element.setPos(x0, y0)
                    self._add_graphics_element(element)

                elif item_type == "Line":
                    parts = item_str.split(":")
                    if len(parts) < 2:
                        continue
                    values = self._parse_key_value_params_float(parts[1].strip())
                    x1 = values.get("x1", 0) * self.scene.step_x * 20 + self.scene.sheet_width / 2
                    y1 = self.scene.sheet_height / 2 - values.get("y1", 0) * self.scene.step_y * 20
                    x2 = values.get("x2", 0) * self.scene.step_x * 20 + self.scene.sheet_width / 2
                    y2 = self.scene.sheet_height / 2 - values.get("y2", 0) * self.scene.step_y * 20
                    line = QGraphicsLineItem(x1, y1, x2, y2)
                    pen = QPen(QColor(0, 0, 0))
                    pen.setWidth(2)
                    line.setPen(pen)
                    self._add_graphics_element(line)

                elif item_type == "Rectangle":
                    parts = item_str.split(":")
                    if len(parts) < 2:
                        continue
                    values = self._parse_key_value_params_float(parts[1].strip())
                    x0 = values.get("x0", 0) * self.scene.step_x * 20 + self.scene.sheet_width / 2
                    y0 = self.scene.sheet_height / 2 - values.get("y0", 0) * self.scene.step_y * 20
                    width = values.get("width", 0) * self.scene.step_x * 20
                    height = values.get("height", 0) * self.scene.step_y * 20
                    rect = QGraphicsRectItem(x0 - width / 2, y0 - height / 2, width, height)
                    pen = QPen(QColor(0, 0, 0))
                    pen.setWidth(2)
                    rect.setPen(pen)
                    self._add_graphics_element(rect)

                elif item_type == "Polygon":
                    parts = item_str.split(":")
                    if len(parts) < 2:
                        continue
                    values = self._parse_key_value_params_float(parts[1].strip())
                    polygon = QPolygonF()
                    i = 1
                    while f"p{i}x" in values and f"p{i}y" in values:
                        x = values[f"p{i}x"] * self.scene.step_x * 20 + self.scene.sheet_width / 2
                        y = self.scene.sheet_height / 2 - values[f"p{i}y"] * self.scene.step_y * 20
                        polygon.append(QPointF(x, y))
                        i += 1
                    if not polygon.isEmpty():
                        poly_item = QGraphicsPolygonItem(polygon)
                        pen = QPen(QColor(0, 0, 0))
                        pen.setWidth(2)
                        poly_item.setPen(pen)
                        poly_item.setBrush(QBrush(QColor(150, 150, 150, 100)))
                        self._add_graphics_element(poly_item)

                elif item_type == "Circle":
                    parts = item_str.split(":")
                    if len(parts) < 2:
                        continue
                    values = self._parse_key_value_params_float(parts[1].strip())
                    x0 = values.get("x0", 0) * self.scene.step_x * 20 + self.scene.sheet_width / 2
                    y0 = self.scene.sheet_height / 2 - values.get("y0", 0) * self.scene.step_y * 20
                    r = values.get("r", 0) * self.scene.step_x * 20
                    circle = QGraphicsEllipseItem(x0 - r, y0 - r, 2 * r, 2 * r)
                    pen = QPen(QColor(0, 0, 0))
                    pen.setWidth(2)
                    circle.setPen(pen)
                    self._add_graphics_element(circle)

            except Exception as e:
                print(f"Error loading geometry item '{item_str}': {e}")
                continue

        self.preview_widget.update_preview(self.scene.symbol_drawlist, self.origin_x, self.origin_y)

    # -----------------------------------------------------------------
    # Geometry serialisation
    # -----------------------------------------------------------------

    def _to_relative_coordinates(self, x: float, y: float) -> tuple:
        """Converts absolute scene pixel coordinates into relative symbolic coordinates."""
        rel_x = (x - self.scene.sheet_width / 2) / (self.scene.step_x * 20)
        rel_y = (self.scene.sheet_height / 2 - y) / (self.scene.step_y * 20)
        return round(rel_x, 3), round(rel_y, 3)

    def _collect_geometry_from_scene(self):
        """Serializes all graphical elements on the canvas into geometry data strings."""
        geometry = []

        point_types = {
            ArrivePoint: "ArrivePoint",
            LeavePoint: "LeavePoint",
            TeePoint: "TeePoint",
            SpindlePoint: "SpindlePoint",
        }

        for item in self.scene.symbol_drawlist:
            for point_class, name in point_types.items():
                if isinstance(item, point_class):
                    rel_x, rel_y = self._to_relative_coordinates(item.x(), item.y())
                    params = [f"x0={rel_x}", f"y0={rel_y}"]

                    if isinstance(item, SpindlePoint) and item.spindle_name:
                        params.append(f"name={item.spindle_name}")

                    if hasattr(item, 'point_type') and item.point_type:
                        params.append(f"type={item.point_type}")

                    geometry.append(f"{name}: {' '.join(params)}")
                    break
            else:
                if isinstance(item, QGraphicsLineItem):
                    x1, y1 = self._to_relative_coordinates(item.line().p1().x(), item.line().p1().y())
                    x2, y2 = self._to_relative_coordinates(item.line().p2().x(), item.line().p2().y())
                    geometry.append(f"Line: x1={x1} y1={y1} x2={x2} y2={y2}")

                elif isinstance(item, QGraphicsRectItem):
                    pos = self.scene.convert_to_relative_position(QPointF(item.rect().x(), item.rect().y()))
                    width = round(item.rect().width() / self.scene.step_x / 20, 2)
                    height = round(item.rect().height() / self.scene.step_x / 20, 2)
                    geometry.append(f"Rectangle: x0={pos.x()} y0={pos.y()} width={width} height={height}")

                elif isinstance(item, QGraphicsPolygonItem):
                    parts = []
                    polygon = item.polygon()
                    for index in range(polygon.count()):
                        point = polygon.at(index)
                        pos = self.scene.convert_to_relative_position(point)
                        parts.append(f"p{index + 1}x={pos.x()} p{index + 1}y={pos.y()}")
                    geometry.append(f"Polygon: {' '.join(parts)}")

        return geometry

    # -----------------------------------------------------------------
    # Legacy raw graphics conversion
    # -----------------------------------------------------------------

    def _parse_geometry_coordinate(self, item, index):
        """Extracts a numeric coordinate value from a formatted geometry parameter string."""
        return round(float(item.split(":")[1].split(" ")[index].split("=")[1]), 3) * 100.0

    def _parse_raw_coordinate_pair(self, geometry: list, index: int) -> tuple:
        """Extracts X and Y floating-point coordinates from a raw geometry data array."""
        return float(geometry[index + 1]), float(geometry[index + 2])

    def _scale_and_offset_point(
        self, x: float, y: float, scale: float, symbol_width: float, symbol_height: float
    ) -> tuple:
        """Scales relative coordinates to scene units and applies centering offsets."""
        scaled_x = round(x * scale - symbol_width / 2, 0) / 100.0
        scaled_y = round(y * scale - symbol_height / 2, 0) / 100.0
        return scaled_x, scaled_y

    def convert_raw_graphics_data(self, skey: str, geometry: list) -> list:
        """Converts legacy numeric graphics codes into the modern geometry string format."""
        self.scene.set_grid_center()

        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')

        for i in range(0, len(geometry), 3):
            code = geometry[i]
            if code in ("1", "2", "3", "6"):
                x, y = self._parse_raw_coordinate_pair(geometry, i)
                min_x, min_y = min(min_x, x), min(min_y, y)
                max_x, max_y = max(max_x, x), max(max_y, y)

        scale = 0.05
        symbol_width = max_x * scale
        symbol_height = max_y * scale

        end_index = len(geometry)
        for i in range(0, len(geometry), 3):
            if geometry[i] == "0":
                end_index = i
                break

        new_geometry = []
        start_x, start_y = 0.0, 0.0
        is_spindle = "SP" in skey

        for i in range(0, len(geometry), 3):
            code = geometry[i]

            if code == "1":
                start_x, start_y = self._parse_raw_coordinate_pair(geometry, i)
                start_x, start_y = self._scale_and_offset_point(
                    start_x, start_y, scale, symbol_width, symbol_height
                )
                if i == 0:
                    point_type = "SpindlePoint" if is_spindle else "ArrivePoint"
                    new_geometry.append(f"{point_type}: x0={start_x} y0={start_y}")
                elif i == len(geometry) - 3 or i == end_index - 3:
                    if not is_spindle:
                        new_geometry.append(f"LeavePoint: x0={start_x} y0={start_y}")

            elif code == "2":
                end_x, end_y = self._parse_raw_coordinate_pair(geometry, i)
                end_x, end_y = self._scale_and_offset_point(
                    end_x, end_y, scale, symbol_width, symbol_height
                )
                new_geometry.append(f"Line: x1={start_x} y1={start_y} x2={end_x} y2={end_y}")
                start_x, start_y = end_x, end_y

            elif code == "3":
                end_x, end_y = self._parse_raw_coordinate_pair(geometry, i)
                end_x, end_y = self._scale_and_offset_point(
                    end_x, end_y, scale, symbol_width, symbol_height
                )
                new_geometry.append(f"TeePoint: x0={end_x} y0={end_y}")
                start_x, start_y = end_x, end_y

            elif code == "6":
                end_x, end_y = self._parse_raw_coordinate_pair(geometry, i)
                end_x, end_y = self._scale_and_offset_point(
                    end_x, end_y, scale, symbol_width, symbol_height
                )
                new_geometry.append(f"SpindlePoint: x0={end_x} y0={end_y}")
                start_x, start_y = end_x, end_y

        return new_geometry

    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------

    @staticmethod
    def _parse_key_value_params(params_str: str) -> dict:
        """Parse 'key=value ...' string into a dict; values are floats where possible."""
        values: dict = {}
        for param in params_str.split():
            if "=" in param:
                key, val = param.split("=", 1)
                try:
                    values[key] = float(val)
                except ValueError:
                    values[key] = val
        return values

    @staticmethod
    def _parse_key_value_params_float(params_str: str) -> dict:
        """Parse 'key=value ...' string into a dict of floats (skips non-numeric)."""
        values: dict = {}
        for param in params_str.split():
            if "=" in param:
                key, val = param.split("=", 1)
                try:
                    values[key] = float(val)
                except ValueError:
                    pass
        return values
