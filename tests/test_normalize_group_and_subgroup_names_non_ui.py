# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

from openiso.controller.db import SkeyDB
from openiso.model.skey import SkeyData


def _load_script_module():
    script_path = Path(__file__).resolve().parents[1] / "data" / "scripts" / "normalize_group_and_subgroup_names.py"
    spec = importlib.util.spec_from_file_location("normalize_group_and_subgroup_names", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_normalize_group_and_subgroup_names_merges_duplicate_spellings(tmp_path):
    db = SkeyDB(str(tmp_path / "openiso_test.db"))

    db.ensure_subgroup_exists("valves", "3_way_valve")
    db.ensure_subgroup_exists("Valves", "3-way valve")
    db.ensure_subgroup_exists("valves", "3_way_valve")
    db.ensure_subgroup_exists("Valves", "3-way valve")
    db.ensure_subgroup_exists("Tees", "Y type tee large")
    db.ensure_subgroup_exists("tees", "y_type_tee_large")

    db.insert_skey(
        SkeyData(
            name="VAL01",
            group_key="valves",
            subgroup_key="3_way_valve",
            description_key="valves.3_way_valve.val01.description",
            geometry=[],
        ),
        user="test",
        comment="create",
    )
    db.insert_skey(
        SkeyData(
            name="VAL02",
            group_key="Valves",
            subgroup_key="3-way valve",
            description_key="Valves.3-way valve.val02.description",
            geometry=[],
        ),
        user="test",
        comment="create",
    )
    db.insert_spindle(
        SkeyData(
            name="SP01",
            group_key="tees",
            subgroup_key="y_type_tee_large",
            description_key="tees.y_type_tee_large.sp01.description",
            geometry=[],
        ),
        user="test",
        comment="create",
    )

    module = _load_script_module()
    result = module.normalize_database(db.db_path)

    assert result["groups"] >= 2
    assert result["subgroups"] >= 2
    assert result["skeys_updated"] >= 1
    assert result["spindles_updated"] >= 1

    conn = sqlite3.connect(db.db_path)
    cur = conn.cursor()

    assert cur.execute("SELECT COUNT(*) FROM skey_groups WHERE skey_group_key = 'Valves'").fetchone()[0] == 1
    assert cur.execute("SELECT COUNT(*) FROM skey_groups WHERE skey_group_key = 'Tees'").fetchone()[0] == 1
    assert cur.execute("SELECT COUNT(*) FROM skeys WHERE skey_group_key = 'Valves'").fetchone()[0] == 2
    assert cur.execute("SELECT COUNT(*) FROM skeys WHERE skey_subgroup_key = '3-way valve'").fetchone()[0] == 2
    assert cur.execute("SELECT COUNT(*) FROM spindles WHERE skey_group_key = 'Tees'").fetchone()[0] == 1

    conn.close()