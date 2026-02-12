"""
Enums for Skey Library models (Orientation, FlowArrow, Dimensioned)
"""
from enum import IntEnum

class Orientation(IntEnum):
    """Skey orientation types"""
    SYMMETRICAL = 0
    NON_SYMMETRICAL = 1
    REDUCERS = 2
    FLANGES = 3

class FlowArrow(IntEnum):
    """Flow arrow display options"""
    DEFAULT = 0
    OFF = 1
    ON = 2

class Dimensioned(IntEnum):
    """Dimensioning options"""
    DEFAULT = 0
    OFF = 1
    ON = 2

class Tracing(IntEnum):
    """Tracing options"""
    DEFAULT = 0
    OFF = 1
    ON = 2

class Insulation(IntEnum):
    """Insulation options"""
    DEFAULT = 0
    OFF = 1
    ON = 2

class IsometricView(IntEnum):
    """Isometric view directions"""
    NE = 0  # North-East (default): X right-up, Y left-up
    NW = 1  # North-West: X left-up, Y right-up
    SE = 2  # South-East: X right-down, Y left-down
    SW = 3  # South-West: X left-down, Y right-down
