# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""User workspace paths for writable runtime data."""

from __future__ import annotations

import ctypes
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WorkspacePaths:
    """Writable user-level paths used by the application at runtime."""

    root: Path
    database_dir: Path
    settings_dir: Path
    database_file: Path
    settings_file: Path


def _default_workspace_root() -> Path:
    """Return hidden workspace directory in the current user profile."""
    return Path.home() / ".openiso"


def _set_hidden_windows(path: Path) -> None:
    """Best-effort hidden attribute on Windows."""
    if os.name != "nt":
        return

    FILE_ATTRIBUTE_HIDDEN = 0x02
    FILE_ATTRIBUTE_DIRECTORY = 0x10

    try:
        current = ctypes.windll.kernel32.GetFileAttributesW(str(path))
        if current == -1:
            return

        hidden_attrs = current | FILE_ATTRIBUTE_HIDDEN
        if path.is_dir():
            hidden_attrs |= FILE_ATTRIBUTE_DIRECTORY
        ctypes.windll.kernel32.SetFileAttributesW(str(path), hidden_attrs)
    except (OSError, AttributeError, ValueError):
        # Hidden attribute is optional; do not fail startup if unavailable.
        return


def ensure_workspace() -> WorkspacePaths:
    """Create workspace directories and return canonical writable paths."""
    root = _default_workspace_root()
    root.mkdir(parents=True, exist_ok=True)
    _set_hidden_windows(root)

    database_dir = root / "database"
    settings_dir = root / "settings"
    database_dir.mkdir(parents=True, exist_ok=True)
    settings_dir.mkdir(parents=True, exist_ok=True)

    settings_file = settings_dir / "openiso.json"

    return WorkspacePaths(
        root=root,
        database_dir=database_dir,
        settings_dir=settings_dir,
        database_file=database_dir / "openiso.db",
        settings_file=settings_file,
    )
