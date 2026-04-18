# SPDX-License-Identifier: MIT

import sqlite3

import pytest

from openiso.controller.db import SkeyDB
from openiso.model.skey import SkeyData


pytestmark = pytest.mark.integration


def _new_db(tmp_path):
    db_path = tmp_path / "openiso_test.db"
    return SkeyDB(str(db_path))


def test_schema_contains_source_and_isogen_columns(tmp_path):
    db = _new_db(tmp_path)
    conn = sqlite3.connect(db.db_path)
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(skeys)")
    skeys_columns = {row[1] for row in cur.fetchall()}

    cur.execute("PRAGMA table_info(spindles)")
    spindles_columns = {row[1] for row in cur.fetchall()}

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='symbol_sources'")
    has_symbol_sources = cur.fetchone() is not None

    conn.close()

    assert has_symbol_sources
    assert "pcf_identification" in skeys_columns
    assert "idf_record" in skeys_columns
    assert "user_definable" in skeys_columns
    assert "flow_dependency" in skeys_columns
    assert "source_id" in skeys_columns
    assert "isogen_standard" in skeys_columns
    assert "source_id" in spindles_columns
    assert "isogen_standard" in spindles_columns


def test_insert_and_read_skey_with_source_metadata(tmp_path):
    db = _new_db(tmp_path)
    db.ensure_subgroup_exists("valves", "gate")

    skey = SkeyData(
        name="VAL01",
        group_key="valves",
        subgroup_key="gate",
        description_key="valves.gate.val01.description",
        orientation=1,
        flow_arrow=2,
        dimensioned=1,
        tracing=2,
        insulation=1,
        pcf_identification="VALVE",
        idf_record="130",
        user_definable=0,
        flow_dependency=1,
        source_name="ISOGEN / Alias Limited",
        source_type="standard",
        source_version="2008",
        isogen_standard=1,
        geometry=["Line: x1=0 y1=0 x2=1 y2=1"],
    )

    created_id = db.insert_skey(skey, user="test", comment="insert")
    all_skeys = db.get_all_skeys()

    assert created_id > 0
    assert len(all_skeys) == 1
    loaded = all_skeys[0]

    assert loaded.name == "VAL01"
    assert loaded.pcf_identification == "VALVE"
    assert loaded.idf_record == "130"
    assert loaded.user_definable == 0
    assert loaded.flow_dependency == 1
    assert loaded.source_name == "ISOGEN / Alias Limited"
    assert loaded.source_type == "standard"
    assert loaded.source_version == "2008"
    assert loaded.isogen_standard == 1
    assert loaded.geometry == ["Line: x1=0 y1=0 x2=1 y2=1"]


def test_update_skey_creates_new_geometry_transaction(tmp_path):
    db = _new_db(tmp_path)
    db.ensure_subgroup_exists("fittings", "tees")

    skey = SkeyData(
        name="TEE01",
        group_key="fittings",
        subgroup_key="tees",
        description_key="fittings.tees.tee01.description",
        geometry=["Line: x1=0 y1=0 x2=1 y2=1"],
    )
    db.insert_skey(skey, user="test", comment="create")

    updated = SkeyData(
        name="TEE01",
        group_key="fittings",
        subgroup_key="tees",
        description_key="fittings.tees.tee01.description",
        geometry=["Line: x1=2 y1=2 x2=3 y2=3"],
    )
    db.update_skey(updated, user="test", comment="edit")

    loaded = db.get_all_skeys()[0]

    assert loaded.name == "TEE01"
    assert loaded.geometry == ["Line: x1=2 y1=2 x2=3 y2=3"]
