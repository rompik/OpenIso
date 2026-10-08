# SPDX-License-Identifier: MIT

from pathlib import Path

import pytest

from openiso.controller.importers import ASCIISkeyImporter, SkeyImporterFactory


pytestmark = pytest.mark.integration


def test_ascii_importer_can_import_sample_skey_file():
    importer = ASCIISkeyImporter()
    result = importer.import_from_file("data/settings/IsoAlgo.skey")

    assert result.success is True
    assert len(result.skeys) > 0
    assert len(result.errors) == 0


def test_ascii_importer_keeps_last_symbol_geometry_with_trailing_blank_lines(tmp_path):
    source_path = Path("data/settings/IsoAlgo.skey")
    expected = ASCIISkeyImporter().import_from_file(str(source_path))
    last_skey_name = next(reversed(expected.skeys))
    assert expected.skeys[last_skey_name].geometry

    import_path = tmp_path / "trailing.skey"
    import_path.write_text(source_path.read_text(encoding="utf-8") + "\n\n", encoding="utf-8")
    result = ASCIISkeyImporter().import_from_file(str(import_path))

    assert result.success is True
    assert result.skeys[last_skey_name].geometry == expected.skeys[last_skey_name].geometry


def test_importer_factory_chooses_by_extension_and_handles_missing_file(tmp_path):
    asc_importer = SkeyImporterFactory.create_importer("symbols.SKEY")
    exported_ascii_importer = SkeyImporterFactory.create_importer("symbols.asc")
    idf_importer = SkeyImporterFactory.create_importer("symbols.idf")

    assert asc_importer.__class__.__name__ == "ASCIISkeyImporter"
    assert exported_ascii_importer.__class__.__name__ == "ASCIISkeyImporter"
    assert idf_importer.__class__.__name__ == "IDFSkeyImporter"

    missing = tmp_path / "missing.skey"
    result = asc_importer.import_from_file(str(missing))

    assert result.success is False
    assert result.skeys == {}
    assert len(result.errors) == 1
