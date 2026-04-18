# SPDX-License-Identifier: MIT

from pathlib import Path

import pytest

from openiso.application import Application


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
