# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""Versioned JSON user settings with controlled migrations."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)

SETTINGS_SCHEMA_VERSION = 3


def _default_settings() -> dict[str, Any]:
    return {
        "config_version": SETTINGS_SCHEMA_VERSION,
        "language": {
            "code": "en",
        },
        "preview": {
            "isometric_view": 2,
            "visible": False,
            "opacity": 0.7,
        },
        "database": {
            "path": "",
        },
    }


class UserSettings:
    """Read/write versioned user settings from JSON file."""

    def __init__(self, json_path: Path):
        self._json_path = json_path
        self._data: dict[str, Any] = {}
        self.load()

    @property
    def path(self) -> Path:
        return self._json_path

    def load(self) -> None:
        self._json_path.parent.mkdir(parents=True, exist_ok=True)

        if self._json_path.exists():
            self._data = self._load_json_file(self._json_path)
        else:
            self._data = _default_settings()
            self.sync()

        self._apply_migrations()

    def get(self, key_path: str, default: Any = None) -> Any:
        parts = [part for part in key_path.split("/") if part]
        node: Any = self._data
        for part in parts:
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def get_str(self, key_path: str, default: str = "") -> str:
        value = self.get(key_path, default)
        return value if isinstance(value, str) else str(value)

    def get_bool(self, key_path: str, default: bool = False) -> bool:
        value = self.get(key_path, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            lowered = value.strip().lower()
            return lowered in ("1", "true", "yes", "on")
        return default

    def get_int(self, key_path: str, default: int = 0) -> int:
        value = self.get(key_path, default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def get_float(self, key_path: str, default: float = 0.0) -> float:
        value = self.get(key_path, default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def set(self, key_path: str, value: Any) -> None:
        parts = [part for part in key_path.split("/") if part]
        if not parts:
            return

        node = self._data
        for part in parts[:-1]:
            child = node.get(part)
            if not isinstance(child, dict):
                child = {}
                node[part] = child
            node = child

        node[parts[-1]] = value

    def sync(self) -> None:
        self._json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = self._data
        payload["config_version"] = SETTINGS_SCHEMA_VERSION

        try:
            with open(self._json_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
        except OSError as err:
            logger.warning("Failed to write settings JSON %s: %s", self._json_path, err)

    def _load_json_file(self, path: Path) -> dict[str, Any]:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                raw = json.load(handle)
            if isinstance(raw, dict):
                return raw
        except (OSError, json.JSONDecodeError) as err:
            logger.warning("Failed to read settings JSON %s: %s", path, err)
        return _default_settings()

    def _apply_migrations(self) -> None:
        """Apply forward migrations one version at a time.

        Keep migration steps explicit so field additions/removals are controlled.
        """
        current_version = self.get_int("config_version", 0)
        migrated = False

        while current_version < SETTINGS_SCHEMA_VERSION:
            next_version = current_version + 1
            self._migrate_one_step(current_version, next_version)
            current_version = next_version
            self._data["config_version"] = current_version
            migrated = True

        if migrated:
            self.sync()

    def _migrate_one_step(self, from_version: int, to_version: int) -> None:
        if from_version == 0 and to_version == 1:
            defaults = _default_settings()
            # Controlled schema initialization. Preserve known values only.
            language_code = self.get_str("language/code", defaults["language"]["code"])
            db_path = self.get_str("database/path", defaults["database"]["path"])
            iso_view = self.get_int("preview/isometric_view", defaults["preview"]["isometric_view"])
            visible = self.get_bool("preview/visible", defaults["preview"]["visible"])
            opacity = self.get_float("preview/opacity", defaults["preview"]["opacity"])

            self._data = defaults
            self.set("language/code", language_code)
            self.set("database/path", db_path)
            self.set("preview/isometric_view", iso_view)
            self.set("preview/visible", visible)
            self.set("preview/opacity", opacity)
            return

        if from_version == 1 and to_version == 2:
            # Migration template for future controlled schema evolution.
            # 1) Read old values that must be preserved or transformed.
            language_code = self.get_str("language/code", "en")
            db_path = self.get_str("database/path", "")
            iso_view = self.get_int("preview/isometric_view", 2)
            visible = self.get_bool("preview/visible", False)
            opacity = self.get_float("preview/opacity", 0.7)

            # 2) Start from clean defaults for target schema version.
            defaults = _default_settings()
            self._data = defaults

            # 3) Re-apply preserved values.
            self.set("language/code", language_code)
            self.set("database/path", db_path)
            self.set("preview/isometric_view", iso_view)
            self.set("preview/visible", visible)
            self.set("preview/opacity", opacity)

            # 4) Template examples for future v2+ edits:
            # Rename field example:
            # old_value = self.get_str("database/path", "")
            # self.set("database/symbols_db_path", old_value)
            #
            # Add new field example:
            # self.set("database/read_only", False)
            #
            # Remove obsolete field example:
            # db_node = self._data.get("database", {})
            # if isinstance(db_node, dict):
            #     db_node.pop("path", None)
            return

        if from_version == 2 and to_version == 3:
            defaults = _default_settings()
            language_code = self.get_str("language/code", "en")
            db_path = self.get_str("database/path", "")
            iso_view = self.get_int("preview/isometric_view", 2)
            visible = self.get_bool("preview/visible", False)
            opacity = self.get_float("preview/opacity", 0.7)

            self._data = defaults
            self.set("language/code", language_code)
            self.set("database/path", db_path)
            self.set("preview/isometric_view", iso_view)
            self.set("preview/visible", visible)
            self.set("preview/opacity", opacity)
            return

        # Future versions should add explicit migration branches above.
        logger.warning("No migration handler from version %d to %d", from_version, to_version)
