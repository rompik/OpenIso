# SPDX-License-Identifier: MIT

from pathlib import Path
import sys

import pytest

from openiso.application import Application
from openiso.__main__ import _ensure_project_root


pytestmark = pytest.mark.smoke


def test_find_data_dir_returns_path_object():
    data_path = Application._find_data_dir()
    assert isinstance(data_path, Path)


def test_application_paths_are_derived_from_pkgdatadir(tmp_path):
    app = Application(pkgdatadir=str(tmp_path))

    assert app.pkgdatadir == Path(tmp_path)
    assert app.icons_dir == Path(tmp_path) / "icons"
    assert app.settings_dir == Path(tmp_path) / "settings"
    assert app.database_dir == Path(tmp_path) / "database"


def test_settings_property_requires_qapplication():
    app = Application(pkgdatadir="/tmp/openiso-tests")

    with pytest.raises(RuntimeError):
        _ = app.settings


def test_entry_point_prioritizes_project_over_installed_package(monkeypatch):
    project_root = str(Path(__file__).resolve().parent.parent)
    package_directory = str(Path(project_root) / "openiso")
    monkeypatch.setattr(sys, "path", [package_directory, project_root, "site-packages"])

    _ensure_project_root()

    assert sys.path[0] == project_root
    assert sys.path.count(project_root) == 1
