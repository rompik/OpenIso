# SPDX-License-Identifier: MIT

import re

import pytest

from openiso.controller.importers import ASCIISkeyImporter
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

    assert lines[0].startswith(" 501 ")
    assert lines[0][5:10].strip() == ""
    assert lines[0][11:15].strip() == "VALV"
    assert lines[0][16:20].strip() == ""
    assert int(lines[0][30:37].strip()) == 2
    assert int(lines[0][38:45].strip()) == 0
    assert int(lines[0][46:53].strip()) == 0

    geometry_lines = [line for line in lines[1:] if line.startswith("502")]
    assert len(geometry_lines) == 3

    # 502 lines must keep fixed internal column layout for legacy ASC parser.
    assert all(len(line) == 103 for line in geometry_lines)

    points: list[tuple[str, float, float]] = []
    for line in geometry_lines:
        triplets = re.findall(r"(\d+)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)", line[5:])
        points.extend((action, float(x), float(y)) for action, x, y in triplets)

    # Keep semantic points before terminator identical.
    first_terminator = points.index(("0", 0.0, 0.0))
    assert points[:first_terminator] == [
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
    ]

    # After first terminator, the line is padded with zero triplets.
    assert all(p == ("0", 0.0, 0.0) for p in points[first_terminator:])


def test_skey_service_export_to_ascii_matches_isoalgo_style_501():
    service = SkeyService(use_db=False)
    skey = SkeyData(
        name="01HT",
        spindle_skey="02SP",
        orientation=0,
        flow_arrow=1,
        dimensioned=1,
        tracing=1,
        insulation=1,
        local_revision=4,
        geometry=[
            "ArrivePoint: x0=-0.5 y0=0.33",
            "LeavePoint: x0=0.5 y0=0.33",
        ],
    )

    exported = service.export_skey_to_ascii(skey)
    lines = exported.splitlines()

    # IsoAlgo-like 501 profile: code in base field, blank new/spindle,
    # and only orientation/local revision preserved.
    assert lines[0].startswith(" 501 ")
    assert len(lines[0]) == 101
    assert lines[0][5:10].strip() == ""
    assert lines[0][11:15].strip() == "01HT"
    assert lines[0][16:20].strip() == ""
    assert int(lines[0][30:37].strip()) == 0
    assert int(lines[0][38:45].strip()) == 0
    assert int(lines[0][46:53].strip()) == 0
    assert int(lines[0][54:61].strip()) == 0
    assert int(lines[0][62:69].strip()) == 0
    assert int(lines[0][94:101].strip()) == 4

    geometry_lines = [line for line in lines[1:] if line.startswith("502")]
    assert geometry_lines
    assert all(len(line) == 103 for line in geometry_lines)


def test_skey_service_exports_circle_geometry_to_ascii(tmp_path):
    service = SkeyService(use_db=False)
    skey = SkeyData(
        name="CIRC",
        geometry=["Circle: x0=0 y0=0 r=1"],
    )
    export_path = tmp_path / "circle.asc"
    export_path.write_text(service.export_skey_to_ascii(skey), encoding="utf-8")

    result = ASCIISkeyImporter().import_from_file(str(export_path))

    assert result.success is True
    assert len([item for item in result.skeys["CIRC"].geometry if item.startswith("Line:")]) == 32


def test_skey_service_export_all_skeys_to_ois_payload_contains_all_fields():
    service = SkeyService(use_db=False)
    service._repository.skeys["M3"] = SkeyData(
        name="M3",
        group_key="Valves",
        subgroup_key="3-Way Valve",
        description_key="",
        spindle_skey="SP01",
        orientation=1,
        flow_arrow=2,
        dimensioned=1,
        tracing=2,
        insulation=1,
        pcf_identification="VALVE",
        idf_record="130",
        user_definable=1,
        flow_dependency=0,
        source_name="OpenIso",
        source_type="standard",
        source_version="1.0",
        isogen_standard=0,
        geometry=["Line: x1=0 y1=0 x2=1 y2=1"],
    )

    payload = service.export_all_skeys_to_ois_payload()

    assert payload["format"] == "openiso-ois"
    assert payload["version"] == 1
    assert "M3" in payload["skeys"]
    assert payload["skeys"]["M3"]["name"] == "M3"
    assert payload["skeys"]["M3"]["group_key"] == "Valves"
    assert payload["skeys"]["M3"]["subgroup_key"] == "3-Way Valve"
    assert payload["skeys"]["M3"]["geometry"] == ["Line: x1=0 y1=0 x2=1 y2=1"]


def test_skey_service_export_all_skeys_to_ascii_contains_each_skey_header():
    service = SkeyService(use_db=False)
    service._repository.skeys["A1"] = SkeyData(
        name="A1",
        spindle_skey="SP01",
        orientation=1,
        flow_arrow=1,
        dimensioned=0,
        geometry=["Line: x1=0 y1=0 x2=1 y2=1"],
    )
    service._repository.skeys["B2"] = SkeyData(
        name="B2",
        spindle_skey="SP02",
        orientation=2,
        flow_arrow=0,
        dimensioned=1,
        geometry=["Line: x1=1 y1=1 x2=2 y2=2"],
    )

    exported = service.export_all_skeys_to_ascii()

    assert " 501 " in exported
    assert "A1" in exported
    assert "B2" in exported
