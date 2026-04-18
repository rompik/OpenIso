# SPDX-License-Identifier: MIT

from pathlib import Path

import pytest

import openiso.core.i18n as i18n
from openiso.controller.services import SkeyService


pytestmark = pytest.mark.integration


def _make_data_path(tmp_path: Path) -> Path:
    data_path = tmp_path / "data"
    (data_path / "database").mkdir(parents=True, exist_ok=True)
    return data_path


def test_service_update_and_delete_skey_non_ui(tmp_path, monkeypatch):
    data_path = _make_data_path(tmp_path)

    # Avoid writing translation files during this non-UI test.
    monkeypatch.setattr(i18n, "save_json_translation", lambda *args, **kwargs: None)

    service = SkeyService(data_path=str(data_path), use_db=True)

    ok = service.update_skey(
        name="VALT1",
        group_key="Valves",
        subgroup_key="Gate",
        description_key="Gate valve",
        spindle_skey="",
        orientation=0,
        flow_arrow=2,
        dimensioned=1,
        tracing=2,
        insulation=1,
        geometry=["Line: x1=0 y1=0 x2=1 y2=1"],
        lang_code="en",
        pcf_identification="VALVE",
        idf_record="130",
        user_definable=1,
        flow_dependency=1,
        source_name="Test Company",
        source_type="company",
        source_version="2026",
        isogen_standard=0,
    )

    assert ok is True
    saved = service.get_skey("VALT1")
    assert saved is not None
    assert saved.group_key == "valves"
    assert saved.subgroup_key == "gate"
    assert saved.pcf_identification == "VALVE"
    assert saved.source_name == "Test Company"

    deleted = service.delete_skey("VALT1")
    assert deleted is True
    assert service.get_skey("VALT1") is None


def test_service_get_subgroups_reads_db(tmp_path):
    data_path = _make_data_path(tmp_path)
    service = SkeyService(data_path=str(data_path), use_db=True)

    service._db.ensure_subgroup_exists("fittings", "elbows")
    service._db.ensure_subgroup_exists("fittings", "tees")

    subgroups = service.get_subgroup_names("fittings")

    assert subgroups == ["elbows", "tees"]
