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


def test_importer_factory_chooses_by_extension_and_handles_missing_file(tmp_path):
    asc_importer = SkeyImporterFactory.create_importer("symbols.SKEY")
    idf_importer = SkeyImporterFactory.create_importer("symbols.idf")

    assert asc_importer.__class__.__name__ == "ASCIISkeyImporter"
    assert idf_importer.__class__.__name__ == "IDFSkeyImporter"

    missing = tmp_path / "missing.skey"
    result = asc_importer.import_from_file(str(missing))

    assert result.success is False
    assert result.skeys == {}
    assert len(result.errors) == 1
