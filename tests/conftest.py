# SPDX-License-Identifier: MIT

"""
Shared pytest fixtures.

The ``isolated_workspace`` fixture is applied automatically to every test.
It replaces the real user workspace (~/.openiso) with a temporary directory so
that every test runs against a fresh, isolated SQLite database and settings
file, preventing cross-test contamination.
"""

from unittest.mock import patch

import pytest

from openiso.core.workspace import WorkspacePaths


@pytest.fixture(autouse=True)
def isolated_workspace(tmp_path):
    """Redirect ensure_workspace() to a per-test temp directory."""
    workspace_root = tmp_path / ".openiso"
    db_dir = workspace_root / "database"
    db_dir.mkdir(parents=True)
    settings_dir = workspace_root / "settings"
    settings_dir.mkdir(parents=True)

    paths = WorkspacePaths(
        root=workspace_root,
        database_dir=db_dir,
        settings_dir=settings_dir,
        database_file=db_dir / "openiso.db",
        settings_file=settings_dir / "settings.json",
    )

    targets = [
        "openiso.controller.services.ensure_workspace",
        "openiso.application.ensure_workspace",
    ]
    with patch(targets[0], return_value=paths), patch(targets[1], return_value=paths):
        yield paths
