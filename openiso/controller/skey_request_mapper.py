# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""Request mappers for Skey save/export operations (UI-independent)."""

from __future__ import annotations


def resolve_skey_name(alias_code: str, skey_name: str) -> str:
    """Resolve effective skey name from alias and regular name fields."""
    alias = (alias_code or "").strip()
    if alias:
        return alias
    return (skey_name or "").strip()


def build_save_payload(form_data: dict, skey_name: str, geometry: list, lang_code: str) -> dict:
    """Build service payload for saving a Skey."""
    return {
        "name": skey_name,
        "group_key": form_data["group_key"],
        "subgroup_key": form_data["subgroup_key"],
        "description_key": form_data["description_text"],
        "spindle_skey": form_data["spindle_skey"],
        "orientation": form_data["orientation"],
        "flow_arrow": form_data["flow_arrow"],
        "dimensioned": form_data["dimensioned"],
        "tracing": form_data["tracing"],
        "insulation": form_data["insulation"],
        "geometry": geometry,
        "lang_code": lang_code,
        "pcf_identification": form_data["pcf_identification"],
        "idf_record": form_data["idf_record"],
        "user_definable": form_data["user_definable"],
        "flow_dependency": form_data["flow_dependency"],
        "source_name": form_data["source_name"],
        "source_type": form_data["source_type"],
        "source_version": form_data["source_version"],
        "isogen_standard": form_data["isogen_standard"],
    }


def build_export_payload(form_data: dict, geometry: list) -> tuple[dict, list]:
    """Build controller payload for exporting a Skey to ASCII."""
    skey_payload = {
        "name": form_data["skey_name"],
        "group_key": form_data["group_key"],
        "subgroup_key": form_data["subgroup_key"],
        "description_key": form_data["description_text"],
        "spindle_skey": form_data["spindle_skey"],
        "orientation": form_data["orientation"],
        "flow_arrow": form_data["flow_arrow"],
        "dimensioned": form_data["dimensioned"],
        "tracing": form_data["tracing"],
        "insulation": form_data["insulation"],
    }
    return skey_payload, geometry
