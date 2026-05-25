# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
import sysconfig

APP_NAME = "OpenIso"
ORG_NAME = "io.github.rompik"
ORG_DOMAIN = "github.io"
DEFAULT_APP_ID = "io.github.rompik.OpenIso"


@dataclass(frozen=True)
class AppPaths:
    data: Path
    icons: Path
    settings: Path
    database: Path

    @classmethod
    def from_data_dir(cls, data_dir: Path) -> "AppPaths":
        return cls(
            data=data_dir,
            icons=data_dir / "icons",
            settings=data_dir / "settings",
            database=data_dir / "database",
        )


def resolve_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_data_dir() -> Path:
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass is not None:
        return Path(meipass) / "data"

    source_data = resolve_project_root() / "data"
    if source_data.exists():
        return source_data

    data_root = sysconfig.get_path("data")
    if data_root:
        candidate = Path(data_root) / "share" / "openiso"
        if candidate.exists():
            return candidate

    prefix_candidate = Path(sys.prefix) / "share" / "openiso"
    if prefix_candidate.exists():
        return prefix_candidate

    for prefix in ("/usr/local", "/usr", str(Path.home() / ".local")):
        candidate = Path(prefix) / "share" / "openiso"
        if candidate.exists():
            return candidate

    return Path.cwd() / "data"


@dataclass(frozen=True)
class AppContext:
    app_id: str
    version: str
    data_dir: Path
    paths: AppPaths

    @classmethod
    def build(
        cls,
        app_id: str,
        version: str,
        pkgdatadir: str | None = None,
    ) -> "AppContext":
        data_dir = Path(pkgdatadir) if pkgdatadir else resolve_data_dir()
        return cls(
            app_id=app_id,
            version=version,
            data_dir=data_dir,
            paths=AppPaths.from_data_dir(data_dir),
        )
