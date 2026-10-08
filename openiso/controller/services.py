# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import hashlib
import json
import logging
import math
import sqlite3
import shutil
from typing import Optional

from openiso.core.app_context import AppContext
from openiso.controller.db import SkeyDB
from openiso.controller.repository import SkeyRepository
from openiso.core.workspace import ensure_workspace
from openiso.model.geometry import GeometryConverter
from openiso.model.skey import SkeyData, SkeyGroup


logger = logging.getLogger(__name__)


class GeometryService:
    """
    Service for geometry-related calculations.
    GUI-independent.
    """
    def __init__(self, settings=None):
        self.settings = settings
        self._converter = GeometryConverter(self.settings) if self.settings else GeometryConverter()

    def parse_geometry_item(self, geometry_string: str) -> dict:
        item_type = geometry_string.split(":")[0]
        result = {"type": item_type}
        if item_type in ("ArrivePoint", "LeavePoint", "TeePoint", "SpindlePoint"):
            result["x0"] = str(GeometryConverter.parse_geometry_value(geometry_string, 1))
            result["y0"] = str(GeometryConverter.parse_geometry_value(geometry_string, 2))
        elif item_type == "Line":
            result["x1"] = str(GeometryConverter.parse_geometry_value(geometry_string, 1))
            result["y1"] = str(GeometryConverter.parse_geometry_value(geometry_string, 2))
            result["x2"] = str(GeometryConverter.parse_geometry_value(geometry_string, 3))
            result["y2"] = str(GeometryConverter.parse_geometry_value(geometry_string, 4))
        elif item_type == "Rectangle":
            result["x0"] = str(GeometryConverter.parse_geometry_value(geometry_string, 1))
            result["y0"] = str(GeometryConverter.parse_geometry_value(geometry_string, 2))
            result["width"] = str(GeometryConverter.parse_geometry_value(geometry_string, 3))
            result["height"] = str(GeometryConverter.parse_geometry_value(geometry_string, 4))
        return result


class SkeyService:
    """
    Main service class that coordinates all Skey business logic.
    This class is completely independent of GUI.
    """
    def __init__(
        self,
        use_db: bool = True,
        context: AppContext | None = None,
        db_path: str | None = None,
    ):
        self._context = context
        if context is not None:
            self._data_dir = context.data_dir
        else:
            self._data_dir = None
        self._repository = SkeyRepository()
        self._geometry_converter = GeometryConverter()
        self._groups = SkeyGroup()
        self._descriptions = {}
        self._use_db = use_db

        workspace = ensure_workspace()
        default_db_path = workspace.database_file

        if self._data_dir is not None:
            seed_db_path = self._data_dir / "database" / "openiso.db"
            if seed_db_path.exists() and not default_db_path.exists():
                try:
                    shutil.copy2(seed_db_path, default_db_path)
                except OSError:
                    logger.debug("Unable to seed workspace database from %s", seed_db_path)

        effective_db_path = db_path.strip() if isinstance(db_path, str) else ""
        self._db = SkeyDB(effective_db_path or str(default_db_path))

        if self._use_db:
            self.load_skeys_from_db()
        elif self._data_dir is not None:
            # Optionally implement loading from JSON if needed
            pass

    def reload_groups(self):
        """Reload skeys from DB and rebuild SkeyGroup from current repository data."""
        self.load_skeys_from_db()

    @property
    def groups(self):
        """Get the current SkeyGroup hierarchy."""
        return self._groups

    def load_descriptions(self) -> bool:
        """Load skey descriptions from the repository."""
        try:
            self._descriptions = self._repository.load_descriptions()
            return True
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as err:
            logger.error("Error loading descriptions: %s", err)
            return False

    def load_skeys_from_db(self) -> bool:
        """Load skeys from the database and update groups."""
        try:
            logger.debug("Loading skeys from database: %s", self._db.db_path)
            skeys = self._db.get_all_skeys()
            logger.debug("Loaded %d skeys from database", len(skeys))
            self._repository.skeys.clear()
            for skey in skeys:
                self._repository.skeys[skey.name] = skey
            self._groups = self._repository.build_groups() if hasattr(self._repository, 'build_groups') else SkeyGroup()
            logger.debug("Built groups with %d top-level groups", len(self._groups.get_groups()))
            return True
        except (sqlite3.Error, OSError, ValueError, TypeError) as err:
            logger.exception("Error loading skeys from DB: %s", err)
            return False

    def load_skeys(self) -> bool:
        """Alias for load_skeys_from_db to match expected interface."""
        return self.load_skeys_from_db()

    def get_sync_conflicts(self) -> list[dict]:
        return self._db.get_sync_conflicts()

    def get_database_path(self) -> str:
        return self._db.db_path

    def switch_database(self, db_path: str) -> bool:
        """Switch active database and reload current in-memory data."""
        if not isinstance(db_path, str) or not db_path.strip():
            return False

        try:
            self._db = SkeyDB(db_path.strip())
            self.load_skeys_from_db()
            return True
        except (sqlite3.Error, OSError, ValueError, TypeError):
            logger.exception("Failed to switch database to %s", db_path)
            return False

    def _normalize_catalog_geometry(self, symbol_code: str, payload: dict) -> list[str]:
        raw_geometry = payload.get("geometry", [])
        if not isinstance(raw_geometry, list):
            return []

        is_legacy_raw_geometry = any(not isinstance(item, str) for item in raw_geometry)
        if not is_legacy_raw_geometry:
            is_legacy_raw_geometry = any(
                isinstance(item, str) and ":" not in item for item in raw_geometry if item
            )

        if is_legacy_raw_geometry:
            return self._geometry_converter.convert_graphics(symbol_code, raw_geometry)

        return [item for item in raw_geometry if isinstance(item, str) and item]

    def _serialize_skey_snapshot(self, skey: SkeyData) -> dict:
        return {
            "name": skey.name,
            "group_key": skey.group_key,
            "subgroup_key": skey.subgroup_key,
            "description_key": skey.description_key,
            "origin_type": skey.origin_type,
            "sync_state": skey.sync_state,
            "orientation": skey.orientation,
            "flow_arrow": skey.flow_arrow,
            "dimensioned": skey.dimensioned,
            "tracing": skey.tracing,
            "insulation": skey.insulation,
            "local_revision": skey.local_revision,
            "upstream_release_version": skey.upstream_release_version,
            "upstream_symbol_version": skey.upstream_symbol_version,
            "geometry": list(skey.geometry),
        }

    def get_sync_conflict_details(self, skey_name: str) -> dict | None:
        local_skey = self.get_skey(skey_name)
        if not local_skey:
            return None

        upstream = None
        upstream_code = local_skey.upstream_symbol_code or local_skey.name
        release_version = local_skey.upstream_release_version
        if release_version:
            catalog_symbol = self._db.get_catalog_symbol(release_version, upstream_code)
            if catalog_symbol:
                upstream_skey = self._build_official_skey(
                    symbol_code=local_skey.name,
                    payload=catalog_symbol["payload"],
                    release_version=release_version,
                    symbol_version=int(catalog_symbol["symbol_version"]),
                    payload_hash=catalog_symbol["payload_hash"],
                )
                upstream_skey.upstream_symbol_code = upstream_code
                upstream = self._serialize_skey_snapshot(upstream_skey)

        local_snapshot = self._serialize_skey_snapshot(local_skey)
        local_geometry = local_snapshot["geometry"]
        upstream_geometry = upstream["geometry"] if upstream else []

        return {
            "name": skey_name,
            "sync_state": local_skey.sync_state,
            "local": local_snapshot,
            "upstream": upstream,
            "summary": {
                "local_geometry_count": len(local_geometry),
                "upstream_geometry_count": len(upstream_geometry),
                "shared_geometry_count": len(set(local_geometry).intersection(upstream_geometry)),
            },
        }

    def _build_official_skey(
        self,
        symbol_code: str,
        payload: dict,
        release_version: str,
        symbol_version: int,
        payload_hash: str,
        *,
        local_revision: int = 1,
    ) -> SkeyData:
        return SkeyData(
            name=symbol_code,
            group_key=payload.get("skey_group") or "unknown",
            subgroup_key=payload.get("subgroup") or "unknown",
            description_key=payload.get("description") or "",
            spindle_skey=payload.get("spindle_skey") or "",
            orientation=int(payload.get("orientation", 0)),
            draw_orientation=int(payload.get("draw_orientation", 0)),
            flow_arrow=int(payload.get("flow_arrow", 0)),
            dimensioned=int(payload.get("dimensioned", 0)),
            tracing=int(payload.get("tracing", 0)),
            insulation=int(payload.get("insulation", 0)),
            geometry=self._normalize_catalog_geometry(symbol_code, payload),
            origin_type="official",
            is_official=1,
            is_user_modified=0,
            upstream_symbol_code=symbol_code,
            upstream_release_version=release_version,
            upstream_symbol_version=symbol_version,
            last_synced_upstream_version=symbol_version,
            upstream_payload_hash=payload_hash,
            local_revision=local_revision,
            sync_state="synced",
        )

    def resolve_sync_conflict_accept_upstream(self, skey_name: str) -> bool:
        existing = self.get_skey(skey_name)
        if not existing:
            return False

        upstream_code = existing.upstream_symbol_code or existing.name
        release_version = existing.upstream_release_version
        if not release_version:
            return False

        catalog_symbol = self._db.get_catalog_symbol(release_version, upstream_code)
        if not catalog_symbol:
            return False

        official_skey = self._build_official_skey(
            symbol_code=existing.name,
            payload=catalog_symbol["payload"],
            release_version=release_version,
            symbol_version=int(catalog_symbol["symbol_version"]),
            payload_hash=catalog_symbol["payload_hash"],
            local_revision=existing.local_revision + 1,
        )
        official_skey.upstream_symbol_code = upstream_code

        self._db.ensure_subgroup_exists(official_skey.group_key, official_skey.subgroup_key)
        self._db.update_skey(official_skey, comment="resolve_accept_upstream")
        self.load_skeys_from_db()
        return True

    def resolve_sync_conflict_keep_local(self, skey_name: str) -> bool:
        existing = self.get_skey(skey_name)
        if not existing:
            return False

        existing.last_synced_upstream_version = existing.upstream_symbol_version
        existing.local_revision += 1
        existing.sync_state = "synced"
        self._db.ensure_subgroup_exists(existing.group_key, existing.subgroup_key)
        self._db.update_skey(existing, comment="resolve_keep_local")
        self.load_skeys_from_db()
        return True

    def sync_official_catalog(self, release_version: str) -> dict:
        """Sync bundled official symbols into user DB without overwriting user content."""
        if self._data_dir is None:
            return {"synced": False, "reason": "no_data_path"}

        catalog_path = self._data_dir / "settings" / "OpenIso.json"
        manifest_path = self._data_dir / "settings" / "OpenIso.catalog.manifest.json"
        if not catalog_path.exists():
            return {"synced": False, "reason": "catalog_missing"}

        manifest_data = {}
        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as manifest_file:
                manifest_data = json.load(manifest_file)

        symbol_versions = manifest_data.get("symbols", {})

        last_synced = self._db.get_metadata("last_synced_release_version")
        if last_synced == release_version:
            return {"synced": False, "reason": "already_synced", "release": release_version}

        with open(catalog_path, "r", encoding="utf-8") as catalog_file:
            catalog_data = json.load(catalog_file)

        stats = {"inserted": 0, "updated": 0, "conflict": 0, "skipped_user": 0}

        for symbol_code, payload in catalog_data.items():
            manifest_entry = symbol_versions.get(symbol_code, {})
            symbol_version = int(manifest_entry.get("version", payload.get("symbol_version", 1)))
            payload_hash = hashlib.sha256(
                json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
            ).hexdigest()

            self._db.upsert_catalog_symbol(
                release_version=release_version,
                symbol_code=symbol_code,
                symbol_version=symbol_version,
                payload_hash=payload_hash,
                payload=payload,
            )

            skey = self._build_official_skey(
                symbol_code=symbol_code,
                payload=payload,
                release_version=release_version,
                symbol_version=symbol_version,
                payload_hash=payload_hash,
            )

            result = self._db.upsert_official_skey(
                skey=skey,
                release_version=release_version,
                upstream_symbol_code=symbol_code,
                upstream_symbol_version=symbol_version,
                upstream_payload_hash=payload_hash,
            )
            if result in stats:
                stats[result] += 1

        self._db.set_metadata("last_synced_release_version", release_version)
        self.load_skeys_from_db()
        return {"synced": True, "release": release_version, **stats}

    def delete_skey(self, skey_name: str) -> bool:
        """Delete a skey from the database and refresh the groups."""
        try:
            self._db.delete_skey(skey_name)
            self.reload_groups()
            return True
        except sqlite3.Error as err:
            logger.error("Error deleting skey '%s': %s", skey_name, err)
            return False

    def get_spindle_geometry(self, spindle_name: str) -> list:
        """Fetch geometry for a given spindle name."""
        return self._db.get_spindle_geometry(spindle_name)

    def get_all_spindles(self) -> list:
        """Fetch all spindles from the database."""
        return self._db.get_all_spindles()

    def filter_groups(self, search_text: str):
        """Filter SkeyGroup by search text."""
        return self._groups.filter(search_text)

    def get_subgroup_names(self, group: str):
        """Get subgroup names for a group from database."""
        db_subgroups = self._db.get_subgroups_by_group(group)
        if db_subgroups:
            return db_subgroups

        return self._groups.get_subgroups(group)

    def get_skey(self, name: str):
        """Get a SkeyData by name."""
        return self._repository.skeys.get(name)

    def update_skey(
        self,
        name: str,
        group_key: str,
        subgroup_key: str,
        description_key: str,
        spindle_skey: str,
        orientation: int,
        flow_arrow: int,
        dimensioned: int,
        tracing: int,
        insulation: int,
        geometry: list,
        lang_code: Optional[str] = None,
        draw_orientation: int = 0,
        pcf_identification: str = "",
        idf_record: str = "",
        user_definable: int = 1,
        flow_dependency: int = 0,
        source_name: str = "",
        source_type: str = "standard",
        source_version: str = "",
        isogen_standard: int = 0,
    ):
        """Update or create a Skey in the database using hierarchical keys."""
        from openiso.core.i18n import save_json_translation


        def clean_key(val):
            if not val:
                return "unknown"
            for prefix in ["group.", "subgroup.", "description."]:
                if val.startswith(prefix):
                    clean_val = val[len(prefix):]
                    # If a path follows the prefix (e.g. description.group.subgroup.name), should we take only the last segment?
                    # No, better to remove only the prefix and keep the path.
                    return clean_val
            return val

        # Preserve display spelling in storage, but keep normalized ids for translation keys.
        group_value = clean_key(group_key)
        subgroup_value = clean_key(subgroup_key)
        g_id = group_value.lower().replace(' ', '_').replace('-', '_')
        sg_id = subgroup_value.lower().replace(' ', '_').replace('-', '_')

        # If we received a display name (not a key), store its translation
        if "." not in group_key:
            save_json_translation(f"{g_id}._name", group_key, lang_code)
        if "." not in subgroup_key:
            save_json_translation(f"{g_id}.{sg_id}._name", subgroup_key, lang_code)

        # Build hierarchical keys for Skey
        name_i18n_key = f"{g_id}.{sg_id}.{name.lower()}"
        desc_i18n_key = f"{name_i18n_key}.description"

        # Save the Skey name translation
        save_json_translation(name_i18n_key, name, lang_code)

        if description_key and "." not in description_key and not description_key.startswith("description."):
            save_json_translation(desc_i18n_key, description_key, lang_code)

        existing = self.get_skey(name)
        if existing:
            if existing.origin_type in ("official", "forked_official"):
                origin_type = "forked_official"
                is_official = 0
                is_user_modified = 1
                sync_state = existing.sync_state
            else:
                origin_type = existing.origin_type
                is_official = existing.is_official
                is_user_modified = existing.is_user_modified
                sync_state = existing.sync_state
            upstream_symbol_code = existing.upstream_symbol_code
            upstream_release_version = existing.upstream_release_version
            upstream_symbol_version = existing.upstream_symbol_version
            last_synced_upstream_version = existing.last_synced_upstream_version
            upstream_payload_hash = existing.upstream_payload_hash
            local_revision = existing.local_revision + 1
        else:
            origin_type = "user"
            is_official = 0
            is_user_modified = 0
            sync_state = "synced"
            upstream_symbol_code = ""
            upstream_release_version = ""
            upstream_symbol_version = 1
            last_synced_upstream_version = 1
            upstream_payload_hash = ""
            local_revision = 1

        skey = SkeyData(
            name=name,
            group_key=group_value,
            subgroup_key=subgroup_value,
            description_key=desc_i18n_key,
            spindle_skey=spindle_skey,
            orientation=orientation,
            draw_orientation=draw_orientation,
            flow_arrow=flow_arrow,
            dimensioned=dimensioned,
            tracing=tracing,
            insulation=insulation,
            pcf_identification=pcf_identification,
            idf_record=idf_record,
            user_definable=user_definable,
            flow_dependency=flow_dependency,
            source_name=source_name,
            source_type=source_type,
            source_version=source_version,
            isogen_standard=isogen_standard,
            origin_type=origin_type,
            is_official=is_official,
            is_user_modified=is_user_modified,
            upstream_symbol_code=upstream_symbol_code,
            upstream_release_version=upstream_release_version,
            upstream_symbol_version=upstream_symbol_version,
            last_synced_upstream_version=last_synced_upstream_version,
            upstream_payload_hash=upstream_payload_hash,
            local_revision=local_revision,
            sync_state=sync_state,
            geometry=geometry
        )

        # Ensure group and subgroup exist in the database
        self._db.ensure_subgroup_exists(group_value, subgroup_value)

        # Update in database
        self._db.update_skey(skey)

        # Update in repository
        self._repository.skeys[name] = skey

        # Rebuild groups
        self._groups = self._repository.build_groups()

        logger.info("Skey '%s' updated successfully with hierarchy: %s -> %s", name, group_value, subgroup_value)
        return True
    def save_skeys(self):
        """Save all skeys (called after updates)."""
        # Data is already saved in database by update_skey
        # This method is for compatibility
        logger.debug("Skeys saved to database")
        return True

    def import_from_ascii(self, file_path: str):
        """Import skeys from ASCII file."""
        from openiso.controller.importers import SkeyImporterFactory
        importer = SkeyImporterFactory.create_importer(file_path, self._descriptions, self._geometry_converter)
        result = importer.import_from_file(file_path)
        if result.success:
            available_spindles = {spindle.name for spindle in self._db.get_all_spindles()}
            for name, skey in result.skeys.items():
                skey.origin_type = "imported"
                skey.is_official = 0
                skey.is_user_modified = 0
                skey.local_revision = 1
                skey.sync_state = "synced"
                if skey.spindle_skey not in available_spindles:
                    skey.spindle_skey = ""
                self._db.ensure_subgroup_exists(skey.group_key, skey.subgroup_key)
                self._db.update_skey(skey)
                self._repository.skeys[name] = skey
            self._groups = self._repository.build_groups()
        return result

    def import_from_idf(self, file_path: str):
        """Import skeys from IDF file."""
        return self.import_from_ascii(file_path)

    def export_skey_to_ascii(self, skey: SkeyData) -> str:
        """
        Convert a SkeyData object to Intergraph ASCII format (lines of 501 and 502 records).
        """
        # 1. Header 501 in IsoAlgo-like fixed-width layout.
        # Keep offsets compatible with importer slices:
        # new(5:10), base(11:15), spindle(16:20), orientation(30:37),
        # flow(38:45), dimensioned(46:53).
        # IsoAlgo-style legacy profile stores symbol code in base field,
        # while keeping new/spindle fields empty.
        skey_name = "".ljust(5)
        base_name = (skey.name[:4]).ljust(4)
        spindle_name = "".ljust(4)

        row_501 = list(" " + "501" + (" " * 97))
        row_501[5:10] = list(skey_name)
        row_501[11:15] = list(base_name)
        row_501[16:20] = list(spindle_name)

        # Legacy base scale field (matches IsoAlgo style).
        row_501[20:30] = list(f"{100:>9} ")

        numeric_values = [
            int(skey.orientation),
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            int(skey.local_revision),
        ]
        starts = [30, 38, 46, 54, 62, 70, 78, 86, 94]
        for start, value in zip(starts, numeric_values):
            row_501[start:start + 7] = list(f"{value:>7}")

        lines = ["".join(row_501)]

        def _to_int_coord(value: float) -> int:
            return int(round(value))

        def _build_502_record(chunk: list[tuple[str, int, int]]) -> str:
            # Keep strict fixed-width layout expected by legacy 502 parser.
            # Slices align with importer positions:
            # (5:14 action, 15:22 x, 23:30 y), ... up to y(95:103).
            row = list("502  " + (" " * 98))
            positions = [
                (5, 14, 15, 22, 23, 30),
                (31, 38, 39, 46, 47, 54),
                (55, 63, 64, 70, 71, 78),
                (79, 86, 87, 94, 95, 103),
            ]

            for (start_action, end_action, start_x, end_x, start_y, end_y), (act, rx, ry) in zip(positions, chunk):
                act_str = str(act).rjust(end_action - start_action)
                x_str = str(rx).rjust(end_x - start_x)
                y_str = str(ry).rjust(end_y - start_y)
                row[start_action:end_action] = list(act_str)
                row[start_x:end_x] = list(x_str)
                row[start_y:end_y] = list(y_str)

            return "".join(row)

        # 2. Geometry 502
        # Convert standardized geometry strings to raw (Action, X, Y)
        # Using scale 20.0 (inverse of 0.05) and an offset of 50.0 to keep coords positive
        raw_geom: list[tuple[str, int, int]] = []
        offset_val = 50.0

        for item in skey.geometry:
            try:
                item_parts = item.split(":", 1)
                item_type = item_parts[0].strip()
                params_str = item_parts[1].strip()

                vals = {}
                for p in params_str.split(" "):
                    if "=" in p:
                        k, v = p.split("=")
                        vals[k] = float(v)

                if item_type in ("ArrivePoint", "LeavePoint", "TeePoint", "SpindlePoint"):
                    action = "1"
                    if item_type == "TeePoint":
                        action = "3"
                    elif item_type == "SpindlePoint":
                        action = "6"
                    raw_geom.append((
                        action,
                        _to_int_coord((vals["x0"] + offset_val) * 20.0),
                        _to_int_coord((vals["y0"] + offset_val) * 20.0),
                    ))
                elif item_type == "Line":
                    raw_geom.append((
                        "1",
                        _to_int_coord((vals["x1"] + offset_val) * 20.0),
                        _to_int_coord((vals["y1"] + offset_val) * 20.0),
                    ))
                    raw_geom.append((
                        "2",
                        _to_int_coord((vals["x2"] + offset_val) * 20.0),
                        _to_int_coord((vals["y2"] + offset_val) * 20.0),
                    ))
                elif item_type == "Rectangle":
                    x, y, w, h = vals["x0"], vals["y0"], vals["width"], vals["height"]
                    rect_pts = [(x - w/2, y - h/2), (x + w/2, y - h/2), (x + w/2, y + h/2), (x - w/2, y + h/2), (x - w/2, y - h/2)]
                    for i, (px, py) in enumerate(rect_pts):
                        act = "1" if i == 0 else "2"
                        raw_geom.append((
                            act,
                            _to_int_coord((px + offset_val) * 20.0),
                            _to_int_coord((py + offset_val) * 20.0),
                        ))
                elif item_type == "Circle":
                    center_x, center_y = vals["x0"], vals["y0"]
                    radius = abs(vals["r"])
                    segment_count = 32
                    for point_index in range(segment_count + 1):
                        angle = 2 * math.pi * point_index / segment_count
                        point_x = center_x + radius * math.cos(angle)
                        point_y = center_y + radius * math.sin(angle)
                        raw_geom.append((
                            "1" if point_index == 0 else "2",
                            _to_int_coord((point_x + offset_val) * 20.0),
                            _to_int_coord((point_y + offset_val) * 20.0),
                        ))
            except (ValueError, IndexError, KeyError):
                continue

        if not raw_geom:
            return "\n".join(lines)

        # 800 terminator
        raw_geom.append(("0", 0, 0))

        # Chunk into fixed-width 502 records (always 4 points per line).
        # If the last chunk is shorter, fill with zero triplets to match legacy formatting.
        for i in range(0, len(raw_geom), 4):
            chunk = raw_geom[i:i+4]
            if len(chunk) < 4:
                chunk.extend([("0", 0, 0)] * (4 - len(chunk)))
            lines.append(_build_502_record(chunk))

        return "\n".join(lines)

    def export_all_skeys_to_ois_payload(self) -> dict:
        """Build OpenIso OIS JSON payload with all Skey parameters from the database."""
        if self._use_db:
            self.load_skeys_from_db()

        skeys_payload: dict[str, dict] = {}
        for skey_name in sorted(self._repository.skeys.keys()):
            skey = self._repository.skeys[skey_name]
            skey_dict = skey.to_dict()
            skey_dict["name"] = skey.name
            skeys_payload[skey_name] = skey_dict

        return {
            "format": "openiso-ois",
            "version": 1,
            "skeys": skeys_payload,
        }

    def export_all_skeys_to_ascii(self) -> str:
        """Export all skeys as a single ASCII text document."""
        if self._use_db:
            self.load_skeys_from_db()

        chunks: list[str] = []
        for skey_name in sorted(self._repository.skeys.keys()):
            skey = self._repository.skeys[skey_name]
            chunks.append(self.export_skey_to_ascii(skey))

        return "\n\n".join(chunks)
