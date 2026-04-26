# SPDX-License-Identifier: MIT

import json
from pathlib import Path

import pytest

import openiso.core.i18n as i18n
from openiso.controller.services import SkeyService


pytestmark = pytest.mark.integration


def _make_data_path(tmp_path: Path) -> Path:
    data_path = tmp_path / "data"
    (data_path / "database").mkdir(parents=True, exist_ok=True)
    (data_path / "settings").mkdir(parents=True, exist_ok=True)
    return data_path


def _write_catalog(data_path: Path, payload: dict) -> None:
    catalog_path = data_path / "settings" / "OpenIso.json"
    catalog_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_manifest(data_path: Path, payload: dict) -> None:
    manifest_path = data_path / "settings" / "OpenIso.catalog.manifest.json"
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_catalog_sync_inserts_official_symbol(tmp_path, monkeypatch):
    data_path = _make_data_path(tmp_path)
    monkeypatch.setattr(i18n, "save_json_translation", lambda *args, **kwargs: None)
    _write_manifest(
        data_path,
        {
            "catalog": "OpenIso",
            "schema_version": 1,
            "release_version": "1.0.0",
            "symbols": {"ABCD": {"version": 7}},
        },
    )

    _write_catalog(
        data_path,
        {
            "ABCD": {
                "skey_group": "Valves",
                "subgroup": "Gate",
                "description": "Gate valve",
                "orientation": 0,
                "flow_arrow": 1,
                "dimensioned": 1,
                "geometry": ["Line: x1=0 y1=0 x2=1 y2=1"],
            }
        },
    )

    service = SkeyService(data_path=str(data_path), use_db=True)
    result = service.sync_official_catalog("1.0.0")
    assert result["synced"] is True
    assert result["inserted"] == 1

    service.load_skeys()
    skey = service.get_skey("ABCD")
    assert skey is not None
    assert skey.origin_type == "official"
    assert skey.is_official == 1
    assert skey.is_user_modified == 0
    assert skey.upstream_release_version == "1.0.0"
    assert skey.upstream_symbol_version == 7


def test_catalog_sync_normalizes_legacy_raw_geometry(tmp_path, monkeypatch):
    data_path = _make_data_path(tmp_path)
    monkeypatch.setattr(i18n, "save_json_translation", lambda *args, **kwargs: None)

    _write_catalog(
        data_path,
        {
            "04HT": {
                "skey_group": "Valves",
                "subgroup": "Gate",
                "description": "Legacy raw geometry",
                "orientation": 0,
                "flow_arrow": 1,
                "dimensioned": 1,
                "geometry": ["1", 0.0, 1000.0, "2", 1000.0, 1000.0, "0", 0.0, 0.0],
            }
        },
    )

    service = SkeyService(data_path=str(data_path), use_db=True)
    result = service.sync_official_catalog("1.0.0")

    assert result["inserted"] == 1
    skey = service.get_skey("04HT")
    assert skey is not None
    assert all(isinstance(item, str) for item in skey.geometry)
    assert any(item.startswith("ArrivePoint:") or item.startswith("SpindlePoint:") for item in skey.geometry)
    assert any(item.startswith("Line:") for item in skey.geometry)


def test_catalog_sync_preserves_user_modified_symbol(tmp_path, monkeypatch):
    data_path = _make_data_path(tmp_path)
    monkeypatch.setattr(i18n, "save_json_translation", lambda *args, **kwargs: None)

    _write_catalog(
        data_path,
        {
            "ABCD": {
                "skey_group": "Valves",
                "subgroup": "Gate",
                "description": "Gate valve",
                "symbol_version": 1,
                "orientation": 0,
                "flow_arrow": 1,
                "dimensioned": 1,
                "geometry": ["Line: x1=0 y1=0 x2=1 y2=1"],
            }
        },
    )

    service = SkeyService(data_path=str(data_path), use_db=True)
    service.sync_official_catalog("1.0.0")

    service.update_skey(
        name="ABCD",
        group_key="valves",
        subgroup_key="gate",
        description_key="edited",
        spindle_skey="",
        orientation=0,
        flow_arrow=1,
        dimensioned=1,
        tracing=0,
        insulation=0,
        geometry=["Line: x1=0 y1=0 x2=2 y2=2"],
        lang_code="en",
    )

    _write_catalog(
        data_path,
        {
            "ABCD": {
                "skey_group": "Valves",
                "subgroup": "Gate",
                "description": "Gate valve updated",
                "symbol_version": 2,
                "orientation": 0,
                "flow_arrow": 1,
                "dimensioned": 1,
                "geometry": ["Line: x1=0 y1=0 x2=3 y2=3"],
            }
        },
    )

    result = service.sync_official_catalog("1.1.0")
    assert result["conflict"] == 1

    service.load_skeys()
    skey = service.get_skey("ABCD")
    assert skey is not None
    assert skey.origin_type == "forked_official"
    assert skey.is_user_modified == 1
    assert skey.sync_state == "conflict"
    assert skey.upstream_symbol_version == 2
    assert "x2=2" in skey.geometry[0]


def test_catalog_sync_skips_user_symbol_with_same_name(tmp_path, monkeypatch):
    data_path = _make_data_path(tmp_path)
    monkeypatch.setattr(i18n, "save_json_translation", lambda *args, **kwargs: None)

    _write_catalog(
        data_path,
        {
            "ABCD": {
                "skey_group": "Valves",
                "subgroup": "Gate",
                "description": "Gate valve",
                "symbol_version": 3,
                "orientation": 0,
                "flow_arrow": 1,
                "dimensioned": 1,
                "geometry": ["Line: x1=0 y1=0 x2=1 y2=1"],
            }
        },
    )

    service = SkeyService(data_path=str(data_path), use_db=True)
    service.update_skey(
        name="ABCD",
        group_key="custom",
        subgroup_key="user",
        description_key="user symbol",
        spindle_skey="",
        orientation=0,
        flow_arrow=0,
        dimensioned=0,
        tracing=0,
        insulation=0,
        geometry=["Line: x1=0 y1=0 x2=5 y2=5"],
        lang_code="en",
    )

    result = service.sync_official_catalog("1.2.0")
    assert result["skipped_user"] == 1

    service.load_skeys()
    skey = service.get_skey("ABCD")
    assert skey is not None
    assert skey.origin_type == "user"
    assert skey.sync_state == "upstream_newer"
    assert skey.upstream_release_version == "1.2.0"
    assert "x2=5" in skey.geometry[0]

    conflicts = service.get_sync_conflicts()
    assert conflicts == [
        {
            "name": "ABCD",
            "origin_type": "user",
            "sync_state": "upstream_newer",
            "upstream_symbol_code": "ABCD",
            "upstream_release_version": "1.2.0",
            "upstream_symbol_version": 3,
        }
    ]


def test_resolve_conflict_accept_upstream_replaces_local_fork(tmp_path, monkeypatch):
    data_path = _make_data_path(tmp_path)
    monkeypatch.setattr(i18n, "save_json_translation", lambda *args, **kwargs: None)

    _write_catalog(
        data_path,
        {
            "ABCD": {
                "skey_group": "Valves",
                "subgroup": "Gate",
                "description": "Gate valve",
                "symbol_version": 1,
                "orientation": 0,
                "flow_arrow": 1,
                "dimensioned": 1,
                "geometry": ["Line: x1=0 y1=0 x2=1 y2=1"],
            }
        },
    )

    service = SkeyService(data_path=str(data_path), use_db=True)
    service.sync_official_catalog("1.0.0")
    service.update_skey(
        name="ABCD",
        group_key="valves",
        subgroup_key="gate",
        description_key="edited",
        spindle_skey="",
        orientation=0,
        flow_arrow=1,
        dimensioned=1,
        tracing=0,
        insulation=0,
        geometry=["Line: x1=0 y1=0 x2=9 y2=9"],
        lang_code="en",
    )

    _write_catalog(
        data_path,
        {
            "ABCD": {
                "skey_group": "Valves",
                "subgroup": "Gate",
                "description": "Gate valve upstream",
                "symbol_version": 2,
                "orientation": 0,
                "flow_arrow": 1,
                "dimensioned": 1,
                "geometry": ["Line: x1=0 y1=0 x2=3 y2=3"],
            }
        },
    )
    service.sync_official_catalog("1.1.0")

    assert service.resolve_sync_conflict_accept_upstream("ABCD") is True

    skey = service.get_skey("ABCD")
    assert skey is not None
    assert skey.origin_type == "official"
    assert skey.is_official == 1
    assert skey.is_user_modified == 0
    assert skey.sync_state == "synced"
    assert skey.upstream_symbol_version == 2
    assert "x2=3" in skey.geometry[0]


def test_get_sync_conflict_details_returns_local_and_upstream_snapshots(tmp_path, monkeypatch):
    data_path = _make_data_path(tmp_path)
    monkeypatch.setattr(i18n, "save_json_translation", lambda *args, **kwargs: None)

    _write_catalog(
        data_path,
        {
            "ABCD": {
                "skey_group": "Valves",
                "subgroup": "Gate",
                "description": "Gate valve",
                "symbol_version": 1,
                "orientation": 0,
                "flow_arrow": 1,
                "dimensioned": 1,
                "geometry": ["Line: x1=0 y1=0 x2=1 y2=1"],
            }
        },
    )

    service = SkeyService(data_path=str(data_path), use_db=True)
    service.sync_official_catalog("1.0.0")
    service.update_skey(
        name="ABCD",
        group_key="valves",
        subgroup_key="gate",
        description_key="edited",
        spindle_skey="",
        orientation=0,
        flow_arrow=1,
        dimensioned=1,
        tracing=0,
        insulation=0,
        geometry=["Line: x1=0 y1=0 x2=9 y2=9"],
        lang_code="en",
    )
    _write_catalog(
        data_path,
        {
            "ABCD": {
                "skey_group": "Valves",
                "subgroup": "Gate",
                "description": "Gate valve upstream",
                "symbol_version": 2,
                "orientation": 0,
                "flow_arrow": 1,
                "dimensioned": 1,
                "geometry": ["Line: x1=0 y1=0 x2=3 y2=3"],
            }
        },
    )
    service.sync_official_catalog("1.1.0")

    details = service.get_sync_conflict_details("ABCD")

    assert details is not None
    assert details["name"] == "ABCD"
    assert details["sync_state"] == "conflict"
    assert details["local"]["origin_type"] == "forked_official"
    assert details["upstream"]["origin_type"] == "official"
    assert details["summary"]["local_geometry_count"] == 1
    assert details["summary"]["upstream_geometry_count"] == 1
    assert details["summary"]["shared_geometry_count"] == 0
    assert "x2=9" in details["local"]["geometry"][0]
    assert "x2=3" in details["upstream"]["geometry"][0]


def test_resolve_conflict_keep_local_acknowledges_upstream(tmp_path, monkeypatch):
    data_path = _make_data_path(tmp_path)
    monkeypatch.setattr(i18n, "save_json_translation", lambda *args, **kwargs: None)

    _write_catalog(
        data_path,
        {
            "ABCD": {
                "skey_group": "Valves",
                "subgroup": "Gate",
                "description": "Gate valve",
                "symbol_version": 1,
                "orientation": 0,
                "flow_arrow": 1,
                "dimensioned": 1,
                "geometry": ["Line: x1=0 y1=0 x2=1 y2=1"],
            }
        },
    )

    service = SkeyService(data_path=str(data_path), use_db=True)
    service.sync_official_catalog("1.0.0")
    service.update_skey(
        name="ABCD",
        group_key="valves",
        subgroup_key="gate",
        description_key="edited",
        spindle_skey="",
        orientation=0,
        flow_arrow=1,
        dimensioned=1,
        tracing=0,
        insulation=0,
        geometry=["Line: x1=0 y1=0 x2=9 y2=9"],
        lang_code="en",
    )

    _write_catalog(
        data_path,
        {
            "ABCD": {
                "skey_group": "Valves",
                "subgroup": "Gate",
                "description": "Gate valve upstream",
                "symbol_version": 2,
                "orientation": 0,
                "flow_arrow": 1,
                "dimensioned": 1,
                "geometry": ["Line: x1=0 y1=0 x2=3 y2=3"],
            }
        },
    )
    service.sync_official_catalog("1.1.0")

    assert service.resolve_sync_conflict_keep_local("ABCD") is True

    skey = service.get_skey("ABCD")
    assert skey is not None
    assert skey.origin_type == "forked_official"
    assert skey.is_user_modified == 1
    assert skey.sync_state == "synced"
    assert skey.last_synced_upstream_version == 2
    assert "x2=9" in skey.geometry[0]
