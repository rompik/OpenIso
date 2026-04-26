# SPDX-License-Identifier: MIT

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

pytestmark = pytest.mark.unit


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def test_canonical_json_schema_is_valid():
    schema_path = _repo_root() / "docs" / "roadmap" / "canonical-symbols-v1.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    # Ensures the schema itself is valid draft-2020-12 JSON Schema.
    Draft202012Validator.check_schema(schema)


def test_example_matches_canonical_json_schema():
    root = _repo_root()
    schema = json.loads((root / "docs" / "roadmap" / "canonical-symbols-v1.schema.json").read_text(encoding="utf-8"))
    payload = json.loads((root / "docs" / "roadmap" / "canonical-symbols-v1.example.json").read_text(encoding="utf-8"))

    Draft202012Validator(schema).validate(payload)
