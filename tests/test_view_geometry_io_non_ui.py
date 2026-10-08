# SPDX-License-Identifier: MIT

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPainterPath
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsRectItem

from openiso.view.main_window.window_geometry_io import GeometryIOMixin


class _TestScene:
    step_x = 5
    step_y = 5
    sheet_width = 1000
    sheet_height = 1000

    def __init__(self, items):
        self.symbol_drawlist = items

    def convert_to_relative_position(self, point):
        return QPointF(
            round((point.x() - self.sheet_width / 2) / (self.step_x * 20), 3),
            round((self.sheet_height / 2 - point.y()) / (self.step_y * 20), 3),
        )


class _TestEditor(GeometryIOMixin):
    def __init__(self, items):
        self.scene = _TestScene(items)


def test_geometry_collection_preserves_rectangles_circles_and_paths():
    rectangle = QGraphicsRectItem(200, 100, 100, 50)
    circle = QGraphicsEllipseItem(100, 100, 50, 50)
    path = QPainterPath()
    path.moveTo(0, 0)
    path.lineTo(100, 100)
    path_item = QGraphicsPathItem(path)

    geometry = GeometryIOMixin._collect_geometry_from_scene(
        _TestEditor([rectangle, circle, path_item])
    )

    assert geometry == [
        "Rectangle: x0=-2.5 y0=3.75 width=1.0 height=0.5",
        "Circle: x0=-3.75 y0=3.75 r=0.25",
        "Line: x1=-5.0 y1=5.0 x2=-4.0 y2=4.0",
    ]