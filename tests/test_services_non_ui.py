# SPDX-License-Identifier: MIT

import pytest

from openiso.controller.services import GeometryService


pytestmark = pytest.mark.unit


def test_geometry_service_parse_line_item():
    service = GeometryService()

    parsed = service.parse_geometry_item("Line: x1=0.10 y1=0.20 x2=0.30 y2=0.40")

    assert parsed == {
        "type": "Line",
        "x1": "10.0",
        "y1": "20.0",
        "x2": "30.0",
        "y2": "40.0",
    }


def test_geometry_service_parse_point_item():
    service = GeometryService()

    parsed = service.parse_geometry_item("ArrivePoint: x0=-0.55 y0=0.75")

    assert parsed["type"] == "ArrivePoint"
    assert float(parsed["x0"]) == pytest.approx(-55.0)
    assert float(parsed["y0"]) == pytest.approx(75.0)
