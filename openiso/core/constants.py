import os
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from openiso.model.enums import IsometricView

# ============================================================================
# OpenIso Constants Module
# ============================================================================
#
# This module centralizes all configuration constants for the OpenIso application,
# including UI dimensions, color themes, and icon paths.
#
# Color Configuration:
# --------------------
# All colors are now centralized in this module for easy customization through
# the settings menu. Color constants are organized into the following categories:
#
# 1. POINT_COLORS - Connection point colors (arrive, leave, tee, spindle)
#                   Also used in preview widget for connection lines
# 2. SCENE_COLORS - Main scene colors (grid, background, highlight, etc.)
# 3. UI_COLORS - UI element colors (buttons, text, links)
# 4. FILL_COLORS_PALETTE - Available fill colors for drawing
# 5. RECENT_FILL_COLORS - Recently used fill colors
#
# To modify colors:
# - Edit the values in this file for global changes
# - Or use the Settings dialog (Colors tab) to customize at runtime
# - Colors use QColor(R, G, B) or hex strings depending on context
#
# Usage Example:
# --------------
#     from openiso.core.constants import SCENE_COLORS, POINT_COLORS
#
#     pen = QPen(SCENE_COLORS["highlight"])
#     arrive_point = ArrivePoint()  # Uses POINT_COLORS["arrive"]
#     # Preview widget also uses POINT_COLORS for arrive/leave lines
# ============================================================================

# UI Constants
BUTTON_SIZE = 36
BUTTON_ICON_SIZE = 36
SMALL_BUTTON_SIZE = 24
SHEET_SIZE = 600
PREVIEW_WIDTH = 300
PREVIEW_HEIGHT = 300

# Isometric View Settings
DEFAULT_ISO_VIEW = IsometricView.NE
ISO_VIEW_NAMES = {
    IsometricView.NE: "North-East (NE)",
    IsometricView.NW: "North-West (NW)",
    IsometricView.SE: "South-East (SE)",
    IsometricView.SW: "South-West (SW)",
}

# Color Theme Configuration
# These colors can be customized through settings

# Point colors (connection points)
POINT_COLORS = {
    "arrive": QColor(51, 51, 255),      # Blue - incoming connection
    "leave": QColor(255, 0, 0),          # Red - outgoing connection
    "tee": Qt.GlobalColor.magenta,       # Magenta - T-junction
    "spindle": QColor(111, 0, 0),        # Dark red - spindle
}

# Scene colors
SCENE_COLORS = {
    "background": QColor(255, 255, 255),     # White - scene background
    "sheet_border": QColor(0, 0, 0),         # Black - sheet border
    "grid_origin": QColor(100, 100, 100),    # Gray - origin lines
    "grid_major": QColor(180, 180, 180),     # Light gray - major grid
    "grid_middle": QColor(210, 210, 210),    # Very light gray - middle grid
    "grid_minor": QColor(230, 230, 230),     # Nearly white - minor grid
    "grid_label": QColor(100, 100, 100),     # Gray - grid labels
    "highlight": QColor(0, 200, 0),          # Green - selection highlight
    "default_pen": QColor(0, 0, 0),          # Black - default drawing pen
}

# UI Element colors (for styling)
UI_COLORS = {
    "button_hover": "#eeeeee",
    "button_border": "#ddd",
    "text_muted": "#888",
    "text_secondary": "#555",
    "terminal_command": "#888",
    "terminal_response": "#005f5f",
    "icon_muted": "#888a85",
    "text_primary": "#2e3436",
    "link_color": "#c01c28",
}

# Fill colors palette (Material Design inspired)
FILL_COLORS_PALETTE = [
    "#FFFFFF", "#000000", "#CCCCCC", "#999999", "#666666", "#333333",
    "#F44336", "#E91E63", "#9C27B0", "#673AB7", "#3F51B5", "#2196F3",
    "#03A9F4", "#00BCD4", "#009688", "#4CAF50", "#8BC34A", "#CDDC39",
    "#FFEB3B", "#FFC107", "#FF9800", "#FF5722", "#795548", "#9E9E9E",
]

# Recent fill colors (default)
RECENT_FILL_COLORS = ["#F44336", "#000000", "#64B5F6", "#1976D2"]

# Links
REPO_URL = "https://github.com/rompik/OpenIso"
ISSUES_URL = f"{REPO_URL}/issues"
NEW_ISSUE_URL = f"{REPO_URL}/issues/new"
README_URL = f"{REPO_URL}#readme"
GPL_LICENSE_URL = "https://www.gnu.org/licenses/gpl-3.0"

# Icon paths configuration
ICONS = {
    # Common/UI Icons
    "about": "common/about.svg",
    "clear_sheet": "common/brush-cleaning.svg",
    "export": "common/export.svg",
    "fill_colors": "common/fill_colors.svg",
    "filter_clear": "common/filter_clear.svg",
    "help": "common/help.svg",
    "import": "common/import.svg",
    "move": "primitives/move.svg",
    "print": "common/printer.svg",
    "redo": "common/128x128_redo.png",
    "rotate": "common/100x100_reload.svg",
    "save": "common/save.svg",
    "scale": "primitives/scale.svg",
    "select_all": "common/select_by_rectangular.svg",
    "select_element": "common/select_element.svg",
    "settings": "common/settings.svg",
    "undo": "common/128x128_undo.png",


    # Connection Points
    "point_arrive": "primitives/128x128_point_arrive.png",
    "point_leave": "primitives/128x128_point_leave.png",
    "point_spindle": "primitives/128x128_point_spindle.png",
    "point_tee": "primitives/128x128_point_tee.png",

    # Primitives - Shapes and Drawing Tools
    "cap": "primitives/128x128_cap.png",
    "circle": "primitives/circle.svg",
    "diamond": "primitives/diamond.svg",
    "hexagon": "primitives/hexagon.svg",
    "line": "primitives/line.svg",
    "polyline": "primitives/polyline.svg",
    "polyline_orthogonal": "primitives/polyline_orthogonal.svg",
    "rectangle": "primitives/rectangle.svg",
    "spline": "primitives/spline.svg",
    "square": "primitives/square.svg",
    "triangle": "primitives/triangle.svg",
}

# Geometry type codes (for ASCII import)
GEOMETRY_CODES = {
    "1": "start_point",
    "2": "line_to",
    "3": "tee_point",
    "6": "spindle_point",
    "0": "end",
}

AVAILABLE_LANGUAGES = [
    ("Русский", "ru"),
    ("Français", "fr"),
    ("中文", "zh_CN"),
    ("English", "en")
]

# Path Constants
# Assuming this file is in src/core/constants.py
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LOCALEDIR = os.path.join(PROJECT_ROOT, 'po')
