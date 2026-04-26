# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

from openiso.controller.skey_request_mapper import (
    build_export_payload,
    build_save_payload,
    resolve_skey_name,
)


def test_resolve_skey_name_prefers_alias():
    assert resolve_skey_name("AL01", "SK01") == "AL01"


def test_resolve_skey_name_falls_back_to_skey_name():
    assert resolve_skey_name("", "SK01") == "SK01"


def test_build_save_payload_maps_fields():
    form_data = {
        "group_key": "group",
        "subgroup_key": "sub",
        "description_text": "desc",
        "spindle_skey": "SP",
        "orientation": 1,
        "flow_arrow": 2,
        "dimensioned": 2,
        "tracing": 1,
        "insulation": 2,
        "pcf_identification": "pcf",
        "idf_record": "idf",
        "user_definable": 1,
        "flow_dependency": 0,
        "source_name": "src",
        "source_type": "standard",
        "source_version": "1.0",
        "isogen_standard": 1,
    }
    geometry = ["Line: x1=0 y1=0 x2=1 y2=1"]

    payload = build_save_payload(form_data, skey_name="SK01", geometry=geometry, lang_code="en")

    assert payload["name"] == "SK01"
    assert payload["group_key"] == "group"
    assert payload["subgroup_key"] == "sub"
    assert payload["geometry"] == geometry
    assert payload["lang_code"] == "en"


def test_build_export_payload_maps_fields():
    form_data = {
        "skey_name": "SK01",
        "group_key": "group",
        "subgroup_key": "sub",
        "description_text": "desc",
        "spindle_skey": "SP",
        "orientation": 1,
        "flow_arrow": 2,
        "dimensioned": 2,
        "tracing": 1,
        "insulation": 2,
    }
    geometry = ["Line: x1=0 y1=0 x2=1 y2=1"]

    skey_payload, geometry_payload = build_export_payload(form_data, geometry)

    assert skey_payload["name"] == "SK01"
    assert skey_payload["group_key"] == "group"
    assert geometry_payload == geometry
