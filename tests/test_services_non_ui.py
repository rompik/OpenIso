# SPDX-License-Identifier: MIT

import re

import pytest

from openiso.controller.services import GeometryService, SkeyService
from openiso.model.skey import SkeyData


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


def test_skey_service_export_to_ascii_produces_expected_records():
    service = SkeyService(use_db=False)
    skey = SkeyData(
        name="VALV1",
        spindle_skey="SP01",
        orientation=2,
        flow_arrow=1,
        dimensioned=0,
        geometry=[
            "ArrivePoint: x0=0.0 y0=0.0",
            "Line: x1=0.0 y1=0.0 x2=1.0 y2=1.0",
            "Rectangle: x0=0.0 y0=0.0 width=2.0 height=2.0",
            "TeePoint: x0=-1.0 y0=2.0",
            "SpindlePoint: x0=3.0 y0=4.0",
        ],
    )

    exported = service.export_skey_to_ascii(skey)
    lines = exported.splitlines()

    assert lines[0].startswith("501  VALV1 VALV SP01")
    assert re.search(r"\s+2\s+1\s+0$", lines[0])

    geometry_lines = [line for line in lines[1:] if line.startswith("502  ")]
    assert len(geometry_lines) == 3

    points: list[tuple[str, float, float]] = []
    for line in geometry_lines:
        triplets = re.findall(r"(\d+)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)", line[5:])
        points.extend((action, float(x), float(y)) for action, x, y in triplets)

    assert points == [
        ("1", 1000.0, 1000.0),
        ("1", 1000.0, 1000.0),
        ("2", 1020.0, 1020.0),
        ("1", 980.0, 980.0),
        ("2", 1020.0, 980.0),
        ("2", 1020.0, 1020.0),
        ("2", 980.0, 1020.0),
        ("2", 980.0, 980.0),
        ("3", 980.0, 1040.0),
        ("6", 1060.0, 1080.0),
        ("0", 0.0, 0.0),
    ]
