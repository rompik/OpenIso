"""
OpenIso - Skey Symbol Library Editor

A GNOME-style application for managing and creating Skey symbols
used in isometric piping drawings.

Main components:
- models: Data classes and enums (SkeyData, SkeyGroup, etc.)
- repository: Data persistence (SkeyRepository)
- geometry: Geometry calculations (GeometryConverter, IsometricProjection)
- importers: File importers (ASCIISkeyImporter, IDFSkeyImporter)
- services: High-level business logic (SkeyService, GeometryService)
- application: Main application class
- window: Main window implementation
"""

import os

# Read version from VERSION file in project root
def _get_version():
    try:
        version_file = os.path.join(os.path.dirname(__file__), '..', 'VERSION')
        print(version_file)
        with open(version_file, 'r') as f:
            return f.read().strip()
    except Exception:
        return '0.5.0'

__version__ = _get_version()
__app_id__ = 'io.github.rompik.OpenIso'

from openiso.model.skey import (
    SkeyData,
    SkeyGroup,
)
from openiso.model.point2d import Point2D
from openiso.model.geometry import GeometryItem, PointGeometry, LineGeometry, RectangleGeometry, PolygonGeometry
from openiso.model.enums import Orientation, FlowArrow, Dimensioned

from openiso.controller.repository import SkeyRepository

from openiso.model.geometry import (
    GeometryConverter,
    GeometrySettings,
    IsometricProjection,
    ArcGeometry,
    HexagonGeometry,
)

from openiso.controller.importers import (
    BaseSkeyImporter,
    ASCIISkeyImporter,
    IDFSkeyImporter,
    SkeyImporterFactory,
    ImportResult,
)

from openiso.controller.services import (
    SkeyService,
    GeometryService,
)

__all__ = [
    '__version__',
    '__app_id__',
    # Models
    'SkeyData',
    'SkeyGroup',
    'Point2D',
    'GeometryItem',
    'PointGeometry',
    'LineGeometry',
    'RectangleGeometry',
    'PolygonGeometry',
    'Orientation',
    'FlowArrow',
    'Dimensioned',
    # Repository
    'SkeyRepository',
    # Geometry
    'GeometryConverter',
    'GeometrySettings',
    'IsometricProjection',
    'ArcGeometry',
    'HexagonGeometry',
    # Importers
    'BaseSkeyImporter',
    'ASCIISkeyImporter',
    'IDFSkeyImporter',
    'SkeyImporterFactory',
    'ImportResult',
    # Services
    'SkeyService',
    'GeometryService',
]
