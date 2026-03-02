# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""
Geometry items module - graphical primitives for connection points.

This module provides classes for different types of connection points used in
isometric piping symbol editing. Each point type has a distinct color to help
users identify connection types.

Classes:
    PointItem: Base class for all connection points
    ArrivePoint: Incoming connection point
    LeavePoint: Outgoing connection point
    TeePoint: T-junction connection point
    SpindlePoint: Spindle connection point
"""

from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtCore import Qt, QRectF
from openiso.core.constants import POINT_COLORS


class PointItem(QGraphicsEllipseItem):
    """
    Base class for connection points.

    Represents a circular connection point with configurable color. Points are
    movable and can be selected by clicking. They are used to mark connection
    locations in the isometric piping symbol.
    """

    def __init__(self, color, point_type=""):
        """
        Initialize a point item.

        Args:
            color (QColor): The color for this point's outline
            point_type (str): The ISOGEN connection type (e.g., BW, SW, FL)
        """
        super().__init__(QRectF(-5.0, -5.0, 10.0, 10.0))
        self.point_type = point_type
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        pen = QPen(color)
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.SolidLine)
        self.setPen(pen)

        if point_type:
            self.setToolTip(f"Type: {point_type}")


class ArrivePoint(PointItem):
    """Incoming connection point"""
    def __init__(self, point_type=""):
        super().__init__(POINT_COLORS["arrive"], point_type)


class LeavePoint(PointItem):
    """Outgoing connection point"""
    def __init__(self, point_type=""):
        super().__init__(POINT_COLORS["leave"], point_type)


class TeePoint(PointItem):
    """T-junction connection point"""
    def __init__(self, point_type=""):
        super().__init__(POINT_COLORS["tee"], point_type)


class SpindlePoint(PointItem):
    """Spindle connection point"""
    def __init__(self, spindle_name="", point_type=""):
        super().__init__(POINT_COLORS["spindle"], point_type)
        self.spindle_name = spindle_name
        if spindle_name:
            self.setToolTip(f"Spindle: {spindle_name}")

# Preview point colors for the mini-preview (mapped by class)
PREVIEW_POINT_COLORS = {
    ArrivePoint: QColor(0, 255, 0),
    LeavePoint: QColor(255, 0, 0),
    TeePoint: QColor(0, 0, 255),
    SpindlePoint: QColor(255, 165, 0),
}

# Note: These are class-mapped colors. For line colors in preview, use CONST_PREVIEW_COLORS from constants

__all__ = [
    'PointItem', 'ArrivePoint', 'LeavePoint', 'TeePoint', 'SpindlePoint',
    'PREVIEW_POINT_COLORS'
]
