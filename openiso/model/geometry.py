# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""
Geometry item base and concrete classes for Skey Library
"""
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
from .point2d import Point2D

@dataclass
class GeometryItem:
    item_type: str
    def to_string(self) -> str:
        raise NotImplementedError

@dataclass
class PointGeometry(GeometryItem):
    x: float
    y: float
    def to_string(self) -> str:
        return f"{self.item_type}: x0={self.x} y0={self.y}"
    @classmethod
    def from_string(cls, s: str) -> 'PointGeometry':
        item_type = s.split(":")[0]
        parts = s.split(":")[1].strip().split(" ")
        x = float(parts[0].split("=")[1])
        y = float(parts[1].split("=")[1])
        return cls(item_type=item_type, x=x, y=y)

@dataclass
class LineGeometry(GeometryItem):
    item_type: str = "Line"
    x1: float = 0.0
    y1: float = 0.0
    x2: float = 0.0
    y2: float = 0.0
    def to_string(self) -> str:
        return f"Line: x1={self.x1} y1={self.y1} x2={self.x2} y2={self.y2}"

    @classmethod
    def from_string(cls, s: str) -> 'LineGeometry':
        parts = s.split(":")[1].strip().split(" ")
        x1 = float(parts[0].split("=")[1])
        y1 = float(parts[1].split("=")[1])
        x2 = float(parts[2].split("=")[1])
        y2 = float(parts[3].split("=")[1])
        return cls(item_type="Line", x1=x1, y1=y1, x2=x2, y2=y2)

@dataclass
class RectangleGeometry(GeometryItem):
    item_type: str = "Rectangle"
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    def to_string(self) -> str:
        return f"Rectangle: x0={self.x} y0={self.y} width={self.width} height={self.height}"
    @classmethod
    def from_string(cls, s: str) -> 'RectangleGeometry':
        parts = s.split(":")[1].strip().split(" ")
        x = float(parts[0].split("=")[1])
        y = float(parts[1].split("=")[1])
        width = float(parts[2].split("=")[1])
        height = float(parts[3].split("=")[1])
        return cls(item_type="Rectangle", x=x, y=y, width=width, height=height)

@dataclass
class PolygonGeometry(GeometryItem):
    item_type: str = "Polygon"
    points: List[Point2D] = field(default_factory=list)
    def to_string(self) -> str:
        parts = []
        for i, point in enumerate(self.points, 1):
            parts.append(f"x{i}={point.x} y{i}={point.y}")
        return f"Polygon: {' '.join(parts)}"


@dataclass
class GeometrySettings:
    """Settings for geometry conversion"""
    origin_x: float = 0.0
    origin_y: float = 0.0


class GeometryConverter:
    """Converts raw geometry data to standardized format"""

    def __init__(self, settings: Optional[GeometrySettings] = None):
        self.settings = settings or GeometrySettings()

    def convert_graphics(self, skey: str, geometry: List) -> List[str]:
        """
        Convert raw geometry data to standardized geometry strings.

        Args:
            skey: Skey name
            geometry: Raw geometry data (list of coordinates)

        Returns:
            List of geometry strings in standardized format
        """
        start_point_x = 0.0
        start_point_y = 0.0
        new_geometry = []
        # Use a fixed scale of 0.05 (1/20) for 100px units
        scale = 0.05
        max_size = 1.0
        max_width = 1.0
        max_height = 1.0
        min_width = 10000.0
        min_height = 10000.0

        # First pass: find bounds
        for x in range(0, len(geometry), 3):
            if geometry[x] in ("1", "2", "3", "6"):
                point_x = float(geometry[x + 1])
                point_y = float(geometry[x + 2])
                min_width = min(point_x, min_width)
                min_height = min(point_y, min_height)
                max_width = max(point_x, max_width)
                max_height = max(point_y, max_height)

        symbol_width = max_width * scale
        symbol_height = max_height * scale

        # Find end of geometry
        index_of_end_geometry = 0
        for x in range(0, len(geometry), 3):
            if geometry[x] == "0":
                index_of_end_geometry = x
                break

        # Second pass: convert geometry
        for x in range(0, len(geometry), 3):
            pen_action = geometry[x]

            if pen_action == "1":
                start_point_x = round(float(geometry[x + 1]) * scale - symbol_width / 2, 3)
                start_point_y = round(float(geometry[x + 2]) * scale - symbol_height / 2, 3)

                if x == 0:
                    point_type = "SpindlePoint" if "SP" in skey else "ArrivePoint"
                    new_geometry.append(f"{point_type}: x0={start_point_x} y0={start_point_y}")
                elif x == (len(geometry) - 3) or x == (index_of_end_geometry - 3):
                    if "SP" not in skey:
                        new_geometry.append(f"LeavePoint: x0={start_point_x} y0={start_point_y}")

            elif pen_action == "2":
                end_point_x = round(float(geometry[x + 1]) * scale - symbol_width / 2, 3)
                end_point_y = round(float(geometry[x + 2]) * scale - symbol_height / 2, 3)
                new_geometry.append(
                    f"Line: x1={start_point_x} y1={start_point_y} x2={end_point_x} y2={end_point_y}"
                )
                start_point_x = end_point_x
                start_point_y = end_point_y

            elif pen_action == "3":
                end_point_x = round(float(geometry[x + 1]) * scale - symbol_width / 2, 3)
                end_point_y = round(float(geometry[x + 2]) * scale - symbol_height / 2, 3)
                new_geometry.append(f"TeePoint: x0={end_point_x} y0={end_point_y}")
                start_point_x = end_point_x
                start_point_y = end_point_y

            elif pen_action == "6":
                end_point_x = round(float(geometry[x + 1]) * scale - symbol_width / 2, 3)
                end_point_y = round(float(geometry[x + 2]) * scale - symbol_height / 2, 3)
                new_geometry.append(f"SpindlePoint: x0={end_point_x} y0={end_point_y}")
                start_point_x = end_point_x
                start_point_y = end_point_y

        return new_geometry

    @staticmethod
    def parse_geometry_value(item: str, index: int) -> float:
        """Parse a coordinate value from geometry string"""
        return round(float(item.split(":")[1].split(" ")[index].split("=")[1]), 3) * 100.0

    @staticmethod
    def convert_to_relative(x: float, y: float,
                            sheet_width: float, sheet_height: float, step: float) -> Tuple[float, float]:
        """Convert scene coordinates to relative position"""
        rel_x = (x - sheet_width / 2) / (step * 20)
        rel_y = (sheet_height / 2 - y) / (step * 20)
        return (round(rel_x, 3), round(rel_y, 3))


class IsometricProjection:
    """Utility class for isometric projection calculations"""

    ISO_ANGLE = math.pi / 6  # 30 degrees

    @classmethod
    def to_isometric(cls, x: float, z: float) -> Tuple[float, float]:
        """
        Convert 3D coordinates (XZ plane) to isometric projection.
        Args:
            x: X coordinate
            z: Z coordinate (depth)
        Returns:
            Tuple of (iso_x, iso_y) for isometric projection
        """
        iso_x = (x - z) * math.cos(cls.ISO_ANGLE)
        iso_y = (x + z) * math.sin(cls.ISO_ANGLE)
        return (iso_x, iso_y)

    @classmethod
    def calculate_bounds(cls, points: List[Tuple[float, float]]) -> Tuple[float, float, float, float]:
        """
        Calculate bounds of isometric points (XZ plane).
        Args:
            points: List of (x, z) tuples
        Returns:
            (min_x, min_y, max_x, max_y) in isometric projection
        """
        if not points:
            return (0, 0, 0, 0)

        iso_points = [cls.to_isometric(x, z) for x, z in points]

        min_x = min(p[0] for p in iso_points)
        min_y = min(p[1] for p in iso_points)
        max_x = max(p[0] for p in iso_points)
        max_y = max(p[1] for p in iso_points)

        return (min_x, min_y, max_x, max_y)

    @classmethod
    def calculate_scale(cls, bounds: Tuple[float, float, float, float],
                        target_width: float, target_height: float,
                        margin: float = 0.8) -> float:
        """Calculate scale factor to fit bounds in target area"""
        min_x, min_y, max_x, max_y = bounds
        width = max_x - min_x or 1
        height = max_y - min_y or 1
        return min(target_width / width, target_height / height) * margin

    @classmethod
    def project_point(cls, x: float, z: float, origin_x: float, origin_z: float,
                      center_x: float, center_y: float, scale: float,
                      preview_cx: float, preview_cy: float) -> Tuple[float, float]:
        """
        Project a point (XZ plane) to isometric view for preview.
        Args:
            x: X coordinate
            z: Z coordinate
            origin_x: Origin X
            origin_z: Origin Z
            center_x: Center X in isometric
            center_y: Center Y in isometric
            scale: Scale factor
            preview_cx: Preview center X
            preview_cy: Preview center Y
        Returns:
            (px, py) projected coordinates
        """
        rel_x = x - origin_x
        rel_z = z - origin_z
        iso_x, iso_y = cls.to_isometric(rel_x, rel_z)
        px = preview_cx + (iso_x - center_x) * scale
        py = preview_cy + (iso_y - center_y) * scale
        return (px, py)


class ArcGeometry:
    """Utility class for arc/curve geometry calculations"""

    @staticmethod
    def create_arc_points(x1: float, y1: float, x2: float, y2: float,
                          segments: int = 20) -> List[Tuple[float, float]]:
        """Create points along a quadratic arc between two points"""
        dx, dy = x2 - x1, y2 - y1
        length = math.sqrt(dx * dx + dy * dy)

        if length > 0:
            nx, ny = -dy / length, dx / length
        else:
            nx, ny = 0, 1

        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        arc_height = length / 2

        # Control point for quadratic bezier
        ctrl_x = mid_x + nx * arc_height
        ctrl_y = mid_y + ny * arc_height

        points = []
        for i in range(segments + 1):
            t = i / segments
            # Quadratic bezier formula
            px = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * ctrl_x + t ** 2 * x2
            py = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * ctrl_y + t ** 2 * y2
            points.append((px, py))

        return points


class HexagonGeometry:
    """Utility class for hexagon geometry calculations"""

    @staticmethod
    def create_hexagon_points(cx: float, cy: float, radius: float) -> List[Tuple[float, float]]:
        """Create points for a regular hexagon"""
        points = []
        for i in range(6):
            angle = math.pi / 3 * i - math.pi / 2  # Start from top
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            points.append((x, y))
        return points

    @staticmethod
    def calculate_radius_from_points(cx: float, cy: float, x: float, y: float) -> float:
        """Calculate radius from center to a point"""
        dx = x - cx
        dy = y - cy
        return math.sqrt(dx * dx + dy * dy)
