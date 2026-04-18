# SPDX-License-Identifier: MIT

import pytest

from openiso.model.geometry import GeometryConverter, PointGeometry
from openiso.model.skey import SkeyData


pytestmark = pytest.mark.unit


def test_skeydata_to_from_dict_roundtrip_with_source_fields():
    source = SkeyData(
        name="VALV1",
        group_key="valves",
        subgroup_key="gate",
        description_key="valves.gate.valv1.description",
        spindle_skey="SP01",
        orientation=2,
        flow_arrow=2,
        dimensioned=1,
        tracing=2,
        insulation=1,
        pcf_identification="VALVE",
        idf_record="130",
        user_definable=0,
        flow_dependency=1,
        source_id=7,
        source_name="MyCompany",
        source_type="company",
        source_version="v2",
        isogen_standard=0,
        geometry=["Line: x1=0 y1=0 x2=1 y2=1"],
    )

    raw = source.to_dict()
    restored = SkeyData.from_dict("VALV1", raw)

    assert restored.name == "VALV1"
    assert restored.group_key == "valves"
    assert restored.subgroup_key == "gate"
    assert restored.pcf_identification == "VALVE"
    assert restored.idf_record == "130"
    assert restored.user_definable == 0
    assert restored.flow_dependency == 1
    assert restored.source_id == 7
    assert restored.source_name == "MyCompany"
    assert restored.source_type == "company"
    assert restored.source_version == "v2"
    assert restored.isogen_standard == 0


def test_geometry_converter_parse_value_and_relative_position():
    value = GeometryConverter.parse_geometry_value(
        "Line: x1=0.15 y1=-0.25 x2=0.45 y2=0.95", 3
    )
    rel = GeometryConverter.convert_to_relative(550.0, 450.0, 1000.0, 1000.0, 5.0)

    assert value == 45.0
    assert rel == (0.5, 0.5)


def test_point_geometry_string_roundtrip():
    point = PointGeometry(item_type="ArrivePoint", x=1.2, y=-3.4)
    encoded = point.to_string()
    decoded = PointGeometry.from_string(encoded)

    assert encoded == "ArrivePoint: x0=1.2 y0=-3.4"
    assert decoded.item_type == "ArrivePoint"
    assert decoded.x == 1.2
    assert decoded.y == -3.4
