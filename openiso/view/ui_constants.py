# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""UI color adapter for converting core color values to QColor objects."""

from __future__ import annotations

from PyQt6.QtGui import QColor

from openiso.core.constants import POINT_COLORS as CORE_POINT_COLORS
from openiso.core.constants import SCENE_COLORS as CORE_SCENE_COLORS


def to_qcolor(value) -> QColor:
    """Convert tuple/hex/QColor values into a QColor instance."""
    if isinstance(value, QColor):
        return QColor(value)
    if isinstance(value, tuple) and len(value) == 3:
        return QColor(*value)
    return QColor(value)


def _build_defaults(source: dict) -> dict:
    return {key: to_qcolor(value) for key, value in source.items()}


POINT_COLORS = _build_defaults(CORE_POINT_COLORS)
SCENE_COLORS = _build_defaults(CORE_SCENE_COLORS)


def update_point_colors(colors: dict) -> None:
    """Update runtime point colors used by UI components."""
    for key, value in colors.items():
        if key in POINT_COLORS:
            POINT_COLORS[key] = to_qcolor(value)


def update_scene_colors(colors: dict) -> None:
    """Update runtime scene colors used by UI components."""
    for key, value in colors.items():
        if key in SCENE_COLORS:
            SCENE_COLORS[key] = to_qcolor(value)


def reset_point_colors() -> None:
    """Reset runtime point colors to defaults from core constants."""
    POINT_COLORS.clear()
    POINT_COLORS.update(_build_defaults(CORE_POINT_COLORS))


def reset_scene_colors() -> None:
    """Reset runtime scene colors to defaults from core constants."""
    SCENE_COLORS.clear()
    SCENE_COLORS.update(_build_defaults(CORE_SCENE_COLORS))
