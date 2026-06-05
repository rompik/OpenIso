# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import contextlib
import os
import json
import logging
import shutil
import sqlite3
from pathlib import Path
from typing import List

from openiso.model.skey import SkeyData
from openiso.core.app_context import resolve_data_dir

DB_PATH = str(resolve_data_dir() / "database" / "openiso.db")

logger = logging.getLogger(__name__)

class SkeyDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = self._resolve_db_path(db_path)
        self._ensure_schema_exists()
        self._ensure_columns_exist()

    def _resolve_db_path(self, db_path: str) -> str:
        """Return a writable DB path, falling back to user-local storage if needed."""
        requested = Path(db_path)
        if self._is_path_writable(requested):
            return str(requested)

        fallback = Path.home() / ".local" / "share" / "openiso" / "database" / "openiso.db"
        fallback.parent.mkdir(parents=True, exist_ok=True)

        # Preserve packaged seed DB when available.
        if requested.exists() and not fallback.exists():
            try:
                shutil.copy2(requested, fallback)
            except OSError:
                pass

        return str(fallback)

    @staticmethod
    def _is_path_writable(path: Path) -> bool:
        """Check whether sqlite DB file can be created/updated at path."""
        parent = path.parent
        try:
            parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            return False

        if not parent.is_dir() or not os.access(parent, os.W_OK):
            return False

        if path.exists() and not os.access(path, os.W_OK):
            return False

        return True

    def _ensure_schema_exists(self):
        """Create minimal schema for first run if DB file is empty/new."""
        with self._transaction() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='skeys'")
            if cur.fetchone() is not None:
                return

            conn.executescript(
                """
            CREATE TABLE IF NOT EXISTS symbol_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                source_type TEXT NOT NULL DEFAULT 'standard',
                version TEXT,
                description TEXT,
                url TEXT,
                CHECK (source_type IN ('standard', 'company', 'project')),
                UNIQUE(name, source_type, version)
            );

            CREATE TABLE IF NOT EXISTS skey_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skey_group_key TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS skey_subgroups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                skey_group_key TEXT NOT NULL,
                skey_subgroup_key TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES skey_groups(id) ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY (skey_group_key) REFERENCES skey_groups(skey_group_key) ON DELETE RESTRICT ON UPDATE CASCADE,
                UNIQUE(group_id, skey_subgroup_key),
                UNIQUE(skey_group_key, skey_subgroup_key)
            );

            CREATE TABLE IF NOT EXISTS spindles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                skey_group_key TEXT NOT NULL,
                skey_subgroup_key TEXT NOT NULL,
                skey_description_key TEXT,
                spindle_skey TEXT,
                orientation INTEGER NOT NULL DEFAULT 0,
                flow_arrow INTEGER NOT NULL DEFAULT 0,
                dimensioned INTEGER NOT NULL DEFAULT 0,
                tracing INTEGER NOT NULL DEFAULT 0,
                insulation INTEGER NOT NULL DEFAULT 0,
                source_id INTEGER,
                isogen_standard INTEGER NOT NULL DEFAULT 0,
                CHECK (orientation IN (0, 1, 2, 3)),
                CHECK (flow_arrow IN (0, 1, 2)),
                CHECK (dimensioned IN (0, 1, 2)),
                CHECK (tracing IN (0, 1, 2)),
                CHECK (insulation IN (0, 1, 2)),
                FOREIGN KEY (skey_group_key) REFERENCES skey_groups(skey_group_key) ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY (skey_group_key, skey_subgroup_key) REFERENCES skey_subgroups(skey_group_key, skey_subgroup_key) ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY (source_id) REFERENCES symbol_sources(id) ON DELETE SET NULL ON UPDATE CASCADE
            );

            CREATE TABLE IF NOT EXISTS skeys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                skey_group_key TEXT NOT NULL,
                skey_subgroup_key TEXT NOT NULL,
                skey_description_key TEXT,
                spindle_skey TEXT,
                orientation INTEGER NOT NULL DEFAULT 0,
                flow_arrow INTEGER NOT NULL DEFAULT 0,
                dimensioned INTEGER NOT NULL DEFAULT 0,
                tracing INTEGER NOT NULL DEFAULT 0,
                insulation INTEGER NOT NULL DEFAULT 0,
                draw_orientation INTEGER NOT NULL DEFAULT 0,
                pcf_identification TEXT,
                idf_record TEXT,
                user_definable INTEGER NOT NULL DEFAULT 1,
                flow_dependency INTEGER NOT NULL DEFAULT 0,
                source_id INTEGER,
                isogen_standard INTEGER NOT NULL DEFAULT 0,
                origin_type TEXT NOT NULL DEFAULT 'official',
                is_official INTEGER NOT NULL DEFAULT 1,
                is_user_modified INTEGER NOT NULL DEFAULT 0,
                upstream_symbol_code TEXT,
                upstream_release_version TEXT,
                upstream_symbol_version INTEGER NOT NULL DEFAULT 1,
                last_synced_upstream_version INTEGER NOT NULL DEFAULT 1,
                upstream_payload_hash TEXT,
                local_revision INTEGER NOT NULL DEFAULT 1,
                sync_state TEXT NOT NULL DEFAULT 'synced',
                CHECK (orientation IN (0, 1, 2, 3)),
                CHECK (flow_arrow IN (0, 1, 2)),
                CHECK (dimensioned IN (0, 1, 2)),
                CHECK (tracing IN (0, 1, 2)),
                CHECK (insulation IN (0, 1, 2)),
                CHECK (draw_orientation IN (0, 1, 2, 3)),
                FOREIGN KEY (skey_group_key) REFERENCES skey_groups(skey_group_key) ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY (skey_group_key, skey_subgroup_key) REFERENCES skey_subgroups(skey_group_key, skey_subgroup_key) ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY (spindle_skey) REFERENCES spindles(name) ON DELETE SET NULL ON UPDATE CASCADE,
                FOREIGN KEY (source_id) REFERENCES symbol_sources(id) ON DELETE SET NULL ON UPDATE CASCADE
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skey_id INTEGER NOT NULL,
                user TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                comment TEXT,
                FOREIGN KEY (skey_id) REFERENCES skeys(id)
            );

            CREATE TABLE IF NOT EXISTS geometry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skey_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                data TEXT NOT NULL,
                transaction_id INTEGER NOT NULL,
                FOREIGN KEY (skey_id) REFERENCES skeys(id),
                FOREIGN KEY (transaction_id) REFERENCES transactions(id)
            );

            CREATE TABLE IF NOT EXISTS spindle_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spindle_id INTEGER NOT NULL,
                user TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                comment TEXT,
                FOREIGN KEY (spindle_id) REFERENCES spindles(id)
            );

            CREATE TABLE IF NOT EXISTS spindle_geometry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spindle_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                data TEXT NOT NULL,
                transaction_id INTEGER NOT NULL,
                FOREIGN KEY (spindle_id) REFERENCES spindles(id),
                FOREIGN KEY (transaction_id) REFERENCES spindle_transactions(id)
            );

            CREATE TABLE IF NOT EXISTS app_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS catalog_symbols (
                release_version TEXT NOT NULL,
                symbol_code TEXT NOT NULL,
                symbol_version INTEGER NOT NULL,
                payload_hash TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                PRIMARY KEY (release_version, symbol_code)
            );

            CREATE INDEX IF NOT EXISTS idx_geometry_skey_txn ON geometry(skey_id, transaction_id);
            CREATE INDEX IF NOT EXISTS idx_transactions_skey ON transactions(skey_id);
            CREATE INDEX IF NOT EXISTS idx_spindle_geometry_spindle_txn ON spindle_geometry(spindle_id, transaction_id);
                """
            )

    @staticmethod
    def _column_exists(cur: sqlite3.Cursor, table: str, column: str) -> bool:
        cur.execute(f"PRAGMA table_info({table})")
        return any(row[1] == column for row in cur.fetchall())

    def _ensure_columns_exist(self):
        """Checks if all necessary columns exist and adds them if missing."""
        with self._transaction() as conn:
            cur = conn.cursor()

            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='skeys'")
            if cur.fetchone() is None:
                return

            try:
                cur.execute("SELECT tracing FROM skeys LIMIT 1")
            except sqlite3.OperationalError:
                logger.info("Adding 'tracing' column to 'skeys' table...")
                try:
                    cur.execute("ALTER TABLE skeys ADD COLUMN tracing INTEGER DEFAULT 0")
                    conn.commit()
                except sqlite3.Error as err:
                    logger.warning("Failed to add 'tracing' column: %s", err)

            try:
                cur.execute("SELECT insulation FROM skeys LIMIT 1")
            except sqlite3.OperationalError:
                logger.info("Adding 'insulation' column to 'skeys' table...")
                try:
                    cur.execute("ALTER TABLE skeys ADD COLUMN insulation INTEGER DEFAULT 0")
                    conn.commit()
                except sqlite3.Error as err:
                    logger.warning("Failed to add 'insulation' column: %s", err)

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS symbol_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    source_type TEXT NOT NULL DEFAULT 'standard',
                    version TEXT,
                    description TEXT,
                    url TEXT,
                    CHECK (source_type IN ('standard', 'company', 'project')),
                    UNIQUE(name, source_type, version)
                )
                """
            )

            new_skey_columns = [
                ("pcf_identification", "TEXT"),
                ("idf_record", "TEXT"),
                ("user_definable", "INTEGER NOT NULL DEFAULT 1"),
                ("flow_dependency", "INTEGER NOT NULL DEFAULT 0"),
                ("source_id", "INTEGER REFERENCES symbol_sources(id) ON DELETE SET NULL"),
                ("isogen_standard", "INTEGER NOT NULL DEFAULT 0"),
                ("origin_type", "TEXT NOT NULL DEFAULT 'official'"),
                ("is_official", "INTEGER NOT NULL DEFAULT 1"),
                ("is_user_modified", "INTEGER NOT NULL DEFAULT 0"),
                ("upstream_symbol_code", "TEXT"),
                ("upstream_release_version", "TEXT"),
                ("upstream_symbol_version", "INTEGER NOT NULL DEFAULT 1"),
                ("last_synced_upstream_version", "INTEGER NOT NULL DEFAULT 1"),
                ("upstream_payload_hash", "TEXT"),
                ("local_revision", "INTEGER NOT NULL DEFAULT 1"),
                ("sync_state", "TEXT NOT NULL DEFAULT 'synced'"),
                ("draw_orientation", "INTEGER NOT NULL DEFAULT 0"),
            ]
            for column_name, column_type in new_skey_columns:
                if not self._column_exists(cur, "skeys", column_name):
                    cur.execute(f"ALTER TABLE skeys ADD COLUMN {column_name} {column_type}")

            new_spindle_columns = [
                ("source_id", "INTEGER REFERENCES symbol_sources(id) ON DELETE SET NULL"),
                ("isogen_standard", "INTEGER NOT NULL DEFAULT 0"),
            ]
            for column_name, column_type in new_spindle_columns:
                if not self._column_exists(cur, "spindles", column_name):
                    cur.execute(f"ALTER TABLE spindles ADD COLUMN {column_name} {column_type}")

            cur.execute(
                """
                INSERT OR IGNORE INTO symbol_sources (id, name, source_type, version, description, url)
                VALUES (1, 'ISOGEN / Alias Limited', 'standard', '2008',
                        'ISOGEN Symbol Key (SKEY) Definitions', 'http://www.alias.ltd.uk')
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS app_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS catalog_symbols (
                    release_version TEXT NOT NULL,
                    symbol_code TEXT NOT NULL,
                    symbol_version INTEGER NOT NULL,
                    payload_hash TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    PRIMARY KEY (release_version, symbol_code)
                )
                """
            )

    def _ensure_symbol_source(self, name: str, source_type: str = "standard", version: str = "") -> int | None:
        source_name = (name or "").strip()
        if not source_name:
            return None

        source_type = (source_type or "standard").strip().lower()
        if source_type not in ("standard", "company", "project"):
            source_type = "standard"

        with self._transaction() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id FROM symbol_sources WHERE name = ? AND source_type = ? AND COALESCE(version, '') = COALESCE(?, '')",
                (source_name, source_type, version),
            )
            row = cur.fetchone()
            if row:
                return row[0]

            cur.execute(
                "INSERT INTO symbol_sources (name, source_type, version) VALUES (?, ?, ?)",
                (source_name, source_type, version),
            )
            return cur.lastrowid

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @contextlib.contextmanager
    def _transaction(self, commit: bool = True):
        """Context manager that opens a connection, optionally commits, and always closes."""
        conn = self.connect()
        try:
            yield conn
            if commit:
                conn.commit()
        finally:
            conn.close()

    def get_metadata(self, key: str) -> str | None:
        with self._transaction(commit=False) as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM app_metadata WHERE key = ?", (key,))
            row = cur.fetchone()
            return row[0] if row else None

    def set_metadata(self, key: str, value: str) -> None:
        with self._transaction() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO app_metadata (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )

    def get_sync_conflicts(self) -> list[dict]:
        with self._transaction(commit=False) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT name, origin_type, sync_state, upstream_symbol_code,
                       upstream_release_version, upstream_symbol_version
                FROM skeys
                WHERE sync_state IN ('conflict', 'upstream_newer')
                ORDER BY name
                """
            )
            rows = cur.fetchall()
            return [
                {
                    "name": row[0],
                    "origin_type": row[1],
                    "sync_state": row[2],
                    "upstream_symbol_code": row[3] or "",
                    "upstream_release_version": row[4] or "",
                    "upstream_symbol_version": row[5] or 1,
                }
                for row in rows
            ]

    def get_catalog_symbol(self, release_version: str, symbol_code: str) -> dict | None:
        with self._transaction(commit=False) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT symbol_version, payload_hash, payload_json
                FROM catalog_symbols
                WHERE release_version = ? AND symbol_code = ?
                """,
                (release_version, symbol_code),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                "symbol_version": row[0],
                "payload_hash": row[1],
                "payload": json.loads(row[2]),
            }

    def upsert_catalog_symbol(
        self,
        release_version: str,
        symbol_code: str,
        symbol_version: int,
        payload_hash: str,
        payload: dict,
    ) -> None:
        with self._transaction() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO catalog_symbols (release_version, symbol_code, symbol_version, payload_hash, payload_json)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(release_version, symbol_code) DO UPDATE SET
                    symbol_version=excluded.symbol_version,
                    payload_hash=excluded.payload_hash,
                    payload_json=excluded.payload_json
                """,
                (release_version, symbol_code, symbol_version, payload_hash, json.dumps(payload, ensure_ascii=False, sort_keys=True)),
            )

    def upsert_official_skey(
        self,
        skey: SkeyData,
        release_version: str,
        upstream_symbol_code: str,
        upstream_symbol_version: int,
        upstream_payload_hash: str,
    ) -> str:
        """Upsert official symbol while preserving user-created and user-modified symbols."""
        self.ensure_subgroup_exists(skey.group_key, skey.subgroup_key)

        with self._transaction() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, origin_type, is_user_modified
                FROM skeys
                WHERE name = ?
                """,
                (skey.name,),
            )
            row = cur.fetchone()

            if not row:
                spindle_skey = skey.spindle_skey or None
                source_id = self._ensure_symbol_source(skey.source_name, skey.source_type, skey.source_version)
                cur.execute(
                    """
                    INSERT INTO skeys (
                        name, skey_group_key, skey_subgroup_key, skey_description_key,
                        spindle_skey, orientation, draw_orientation, flow_arrow, dimensioned, tracing, insulation,
                        pcf_identification, idf_record, user_definable, flow_dependency,
                        source_id, isogen_standard,
                        origin_type, is_official, is_user_modified,
                        upstream_symbol_code, upstream_release_version,
                        upstream_symbol_version, last_synced_upstream_version,
                        upstream_payload_hash, local_revision, sync_state
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        skey.name, skey.group_key, skey.subgroup_key, skey.description_key,
                        spindle_skey, skey.orientation, skey.draw_orientation, skey.flow_arrow, skey.dimensioned,
                        skey.tracing, skey.insulation, skey.pcf_identification, skey.idf_record,
                        skey.user_definable, skey.flow_dependency, source_id, skey.isogen_standard,
                        "official", 1, 0,
                        upstream_symbol_code, release_version,
                        upstream_symbol_version, upstream_symbol_version,
                        upstream_payload_hash, 1, "synced",
                    ),
                )
                skey_id = cur.lastrowid
                cur.execute(
                    "INSERT INTO transactions (skey_id, user, action, comment) VALUES (?, ?, ?, ?)",
                    (skey_id, "system", "create", f"official sync {release_version}"),
                )
                transaction_id = cur.lastrowid
                for geom in skey.geometry:
                    cur.execute(
                        "INSERT INTO geometry (skey_id, type, data, transaction_id) VALUES (?, ?, ?, ?)",
                        (skey_id, geom.split(":")[0], geom, transaction_id),
                    )
                return "inserted"

            skey_id, origin_type, is_user_modified = row

            if origin_type in ("user", "imported"):
                cur.execute(
                    """
                    UPDATE skeys
                    SET upstream_symbol_code = ?,
                        upstream_release_version = ?,
                        upstream_symbol_version = ?,
                        upstream_payload_hash = ?,
                        sync_state = 'upstream_newer'
                    WHERE id = ?
                    """,
                    (upstream_symbol_code, release_version, upstream_symbol_version, upstream_payload_hash, skey_id),
                )
                return "skipped_user"

            if is_user_modified:
                cur.execute(
                    """
                    UPDATE skeys
                    SET upstream_symbol_code = ?,
                        upstream_release_version = ?,
                        upstream_symbol_version = ?,
                        upstream_payload_hash = ?,
                        sync_state = 'conflict'
                    WHERE id = ?
                    """,
                    (upstream_symbol_code, release_version, upstream_symbol_version, upstream_payload_hash, skey_id),
                )
                return "conflict"

            spindle_skey = skey.spindle_skey or None
            source_id = self._ensure_symbol_source(skey.source_name, skey.source_type, skey.source_version)
            cur.execute(
                """
                UPDATE skeys SET
                    skey_group_key = ?,
                    skey_subgroup_key = ?,
                    skey_description_key = ?,
                    spindle_skey = ?,
                    orientation = ?,
                    draw_orientation = ?,
                    flow_arrow = ?,
                    dimensioned = ?,
                    tracing = ?,
                    insulation = ?,
                    pcf_identification = ?,
                    idf_record = ?,
                    user_definable = ?,
                    flow_dependency = ?,
                    source_id = ?,
                    isogen_standard = ?,
                    origin_type = 'official',
                    is_official = 1,
                    is_user_modified = 0,
                    upstream_symbol_code = ?,
                    upstream_release_version = ?,
                    upstream_symbol_version = ?,
                    last_synced_upstream_version = ?,
                    upstream_payload_hash = ?,
                    sync_state = 'synced'
                WHERE id = ?
                """,
                (
                    skey.group_key, skey.subgroup_key, skey.description_key,
                    spindle_skey, skey.orientation, skey.draw_orientation, skey.flow_arrow, skey.dimensioned,
                    skey.tracing, skey.insulation,
                    skey.pcf_identification, skey.idf_record, skey.user_definable,
                    skey.flow_dependency, source_id, skey.isogen_standard,
                    upstream_symbol_code, release_version, upstream_symbol_version,
                    upstream_symbol_version, upstream_payload_hash,
                    skey_id,
                ),
            )
            cur.execute(
                "INSERT INTO transactions (skey_id, user, action, comment) VALUES (?, ?, ?, ?)",
                (skey_id, "system", "edit", f"official sync {release_version}"),
            )
            transaction_id = cur.lastrowid
            for geom in skey.geometry:
                cur.execute(
                    "INSERT INTO geometry (skey_id, type, data, transaction_id) VALUES (?, ?, ?, ?)",
                    (skey_id, geom.split(":")[0], geom, transaction_id),
                )
            return "updated"

    def _migrate_spindle_anchor_points(self):
        """One-time migration: replace SpindlePoint with ArrivePoint for spindle symbols."""
        with self._transaction() as conn:
            cur = conn.cursor()
            # Check if migration has already been done
            cur.execute("SELECT value FROM app_metadata WHERE key = 'spindle_anchor_migration_done'")
            row = cur.fetchone()
            if row:
                return  # Migration already executed

            # Execute migration
            cur.execute(
                """
                UPDATE geometry SET data = REPLACE(data, 'SpindlePoint:', 'ArrivePoint:')
                WHERE skey_id IN (
                    SELECT s.id FROM skeys s
                    WHERE s.name IN (SELECT name FROM spindles)
                       OR UPPER(s.name) LIKE '%SP'
                )
                AND data LIKE 'SpindlePoint:%'
                """
            )

            # Mark migration as done
            cur.execute(
                "INSERT OR REPLACE INTO app_metadata (key, value) VALUES (?, ?)",
                ("spindle_anchor_migration_done", "true"),
            )

    def get_all_skeys(self) -> List[SkeyData]:
        # Execute spindle anchor migration if needed
        self._migrate_spindle_anchor_points()

        # All columns are guaranteed by _ensure_columns_exist() called at __init__.
        # sqlite3.Row allows named column access, eliminating index tracking.
        with self._transaction(commit=False) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                """
                SELECT
                    s.id, s.name, s.skey_group_key, s.skey_subgroup_key, s.skey_description_key,
                    s.spindle_skey, s.orientation, s.draw_orientation, s.flow_arrow, s.dimensioned, s.tracing, s.insulation,
                    s.pcf_identification, s.idf_record, s.user_definable, s.flow_dependency,
                    s.source_id, s.isogen_standard, s.origin_type, s.is_official, s.is_user_modified,
                    s.upstream_symbol_code, s.upstream_release_version, s.upstream_symbol_version,
                    s.last_synced_upstream_version, s.upstream_payload_hash, s.local_revision, s.sync_state,
                    COALESCE(ss.name, '')             AS source_name,
                    COALESCE(ss.source_type, 'standard') AS source_type,
                    COALESCE(ss.version, '')          AS source_version
                FROM skeys s
                LEFT JOIN symbol_sources ss ON ss.id = s.source_id
                ORDER BY s.name
                """
            )
            rows = cur.fetchall()
            return [
                SkeyData(
                    name=row["name"],
                    group_key=row["skey_group_key"],
                    subgroup_key=row["skey_subgroup_key"],
                    description_key=row["skey_description_key"],
                    spindle_skey=row["spindle_skey"] or "",
                    orientation=row["orientation"],
                    draw_orientation=row["draw_orientation"],
                    flow_arrow=row["flow_arrow"],
                    dimensioned=row["dimensioned"],
                    tracing=row["tracing"],
                    insulation=row["insulation"],
                    pcf_identification=row["pcf_identification"] or "",
                    idf_record=row["idf_record"] or "",
                    user_definable=row["user_definable"],
                    flow_dependency=row["flow_dependency"],
                    source_id=row["source_id"],
                    source_name=row["source_name"],
                    source_type=row["source_type"],
                    source_version=row["source_version"],
                    isogen_standard=row["isogen_standard"],
                    origin_type=row["origin_type"],
                    is_official=row["is_official"],
                    is_user_modified=row["is_user_modified"],
                    upstream_symbol_code=row["upstream_symbol_code"] or "",
                    upstream_release_version=row["upstream_release_version"] or "",
                    upstream_symbol_version=row["upstream_symbol_version"],
                    last_synced_upstream_version=row["last_synced_upstream_version"],
                    upstream_payload_hash=row["upstream_payload_hash"] or "",
                    local_revision=row["local_revision"],
                    sync_state=row["sync_state"],
                    geometry=self.get_latest_geometry_for_skey(row["id"]),
                )
                for row in rows
            ]

    def get_latest_geometry_for_skey(self, skey_id: int) -> List[str]:
        with self._transaction(commit=False) as conn:
            cur = conn.cursor()
            cur.execute("SELECT MAX(transaction_id) FROM geometry WHERE skey_id = ?", (skey_id,))
            row = cur.fetchone()
            if not row or row[0] is None:
                return []
            transaction_id = row[0]
            cur.execute("SELECT data FROM geometry WHERE skey_id = ? AND transaction_id = ? ORDER BY id ASC", (skey_id, transaction_id))
            return [r[0] for r in cur.fetchall()]

    def insert_skey(self, skey: SkeyData, user: str = "system", comment: str = "create") -> int:
        spindle_skey = skey.spindle_skey or None  # '' -> NULL for proper FK behavior
        source_id = skey.source_id if skey.source_id is not None else self._ensure_symbol_source(
            skey.source_name, skey.source_type, skey.source_version
        )
        with self._transaction() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO skeys (
                    name, skey_group_key, skey_subgroup_key, skey_description_key,
                    spindle_skey, orientation, draw_orientation, flow_arrow, dimensioned, tracing, insulation,
                    pcf_identification, idf_record, user_definable, flow_dependency,
                    source_id, isogen_standard,
                    origin_type, is_official, is_user_modified,
                    upstream_symbol_code, upstream_release_version,
                    upstream_symbol_version, last_synced_upstream_version,
                    upstream_payload_hash, local_revision, sync_state
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    skey.name, skey.group_key, skey.subgroup_key, skey.description_key,
                    spindle_skey, skey.orientation, skey.draw_orientation, skey.flow_arrow, skey.dimensioned,
                    skey.tracing, skey.insulation,
                    skey.pcf_identification, skey.idf_record, skey.user_definable,
                    skey.flow_dependency, source_id, skey.isogen_standard,
                    skey.origin_type, skey.is_official, skey.is_user_modified,
                    skey.upstream_symbol_code, skey.upstream_release_version,
                    skey.upstream_symbol_version, skey.last_synced_upstream_version,
                    skey.upstream_payload_hash, skey.local_revision, skey.sync_state,
                ),
            )
            skey_id = cur.lastrowid
            cur.execute("INSERT INTO transactions (skey_id, user, action, comment) VALUES (?, ?, ?, ?)", (skey_id, user, "create", comment))
            transaction_id = cur.lastrowid
            for geom in skey.geometry:
                cur.execute("INSERT INTO geometry (skey_id, type, data, transaction_id) VALUES (?, ?, ?, ?)", (skey_id, geom.split(":")[0], geom, transaction_id))
            return skey_id if skey_id is not None else 0

    def delete_skey(self, skey_name: str):
        with self._transaction() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM skeys WHERE name = ?", (skey_name,))
            row = cur.fetchone()
            if row:
                skey_id = row[0]
                cur.execute("DELETE FROM geometry WHERE skey_id = ?", (skey_id,))
                cur.execute("DELETE FROM transactions WHERE skey_id = ?", (skey_id,))
                cur.execute("DELETE FROM skeys WHERE id = ?", (skey_id,))

    def update_skey(self, skey: SkeyData, user: str = "system", comment: str = "edit"):
        spindle_skey = skey.spindle_skey or None  # '' → NULL
        source_id = skey.source_id if skey.source_id is not None else self._ensure_symbol_source(
            skey.source_name, skey.source_type, skey.source_version
        )
        with self._transaction() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM skeys WHERE name = ?", (skey.name,))
            row = cur.fetchone()
            if not row:
                return self.insert_skey(skey, user, comment)
            skey_id = row[0]
            cur.execute(
                """
                UPDATE skeys SET
                    skey_group_key = ?,
                    skey_subgroup_key = ?,
                    skey_description_key = ?,
                    spindle_skey = ?,
                    orientation = ?,
                    draw_orientation = ?,
                    flow_arrow = ?,
                    dimensioned = ?,
                    tracing = ?,
                    insulation = ?,
                    pcf_identification = ?,
                    idf_record = ?,
                    user_definable = ?,
                    flow_dependency = ?,
                    source_id = ?,
                    isogen_standard = ?,
                    origin_type = ?,
                    is_official = ?,
                    is_user_modified = ?,
                    upstream_symbol_code = ?,
                    upstream_release_version = ?,
                    upstream_symbol_version = ?,
                    last_synced_upstream_version = ?,
                    upstream_payload_hash = ?,
                    local_revision = ?,
                    sync_state = ?
                WHERE id = ?
                """,
                (
                    skey.group_key, skey.subgroup_key, skey.description_key,
                    spindle_skey, skey.orientation, skey.draw_orientation, skey.flow_arrow, skey.dimensioned,
                    skey.tracing, skey.insulation,
                    skey.pcf_identification, skey.idf_record, skey.user_definable,
                    skey.flow_dependency, source_id, skey.isogen_standard,
                    skey.origin_type, skey.is_official, skey.is_user_modified,
                    skey.upstream_symbol_code, skey.upstream_release_version,
                    skey.upstream_symbol_version, skey.last_synced_upstream_version,
                    skey.upstream_payload_hash, skey.local_revision, skey.sync_state,
                    skey_id,
                ),
            )
            cur.execute("INSERT INTO transactions (skey_id, user, action, comment) VALUES (?, ?, ?, ?)", (skey_id, user, "edit", comment))
            transaction_id = cur.lastrowid
            for geom in skey.geometry:
                cur.execute("INSERT INTO geometry (skey_id, type, data, transaction_id) VALUES (?, ?, ?, ?)", (skey_id, geom.split(":")[0], geom, transaction_id))
            return skey_id if skey_id is not None else 0

    def get_spindle_geometry(self, spindle_name: str) -> List[str]:
        with self._transaction(commit=False) as conn:
            cur = conn.cursor()
            try:
                cur.execute("SELECT id FROM spindles WHERE name = ?", (spindle_name,))
                row = cur.fetchone()
                if not row:
                    return []
                spindle_id = row[0]

                cur.execute("SELECT MAX(transaction_id) FROM spindle_geometry WHERE spindle_id = ?", (spindle_id,))
                trans_row = cur.fetchone()
                if not trans_row or trans_row[0] is None:
                    return []
                transaction_id = trans_row[0]

                cur.execute("SELECT data FROM spindle_geometry WHERE spindle_id = ? AND transaction_id = ? ORDER BY id ASC",
                           (spindle_id, transaction_id))
                return [r[0] for r in cur.fetchall()]
            except sqlite3.OperationalError:
                return []

    def get_all_spindles(self) -> List[SkeyData]:
        """Returns all spindles as SkeyData objects from the database."""
        spindles = []
        with self._transaction(commit=False) as conn:
            cur = conn.cursor()
            try:
                cur.execute("""
                    SELECT id, name, skey_group_key, skey_subgroup_key, skey_description_key,
                           spindle_skey, orientation, flow_arrow, dimensioned, tracing, insulation
                    FROM spindles ORDER BY name
                """)
                rows = cur.fetchall()
                for row in rows:
                    _, name, group_key, subgroup_key, desc_key, s_skey, orient, flow, dim, tracing, insul = row
                    geometry = self.get_spindle_geometry(name)
                    spindles.append(SkeyData(
                        name=name,
                        group_key=group_key,
                        subgroup_key=subgroup_key,
                        description_key=desc_key,
                        spindle_skey=s_skey,
                        orientation=orient,
                        flow_arrow=flow,
                        dimensioned=dim,
                        tracing=tracing,
                        insulation=insul,
                        geometry=geometry
                    ))
            except sqlite3.OperationalError:
                # Table may be missing or have an outdated structure
                self._init_spindles_table(conn)
        return spindles

    def insert_spindle(self, spindle: SkeyData, user: str = "system", comment: str = "create") -> int:
        """Inserts a new spindle into the database (similar to Skey)."""
        spindle_skey = spindle.spindle_skey or None  # '' → NULL
        with self._transaction() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO spindles (name, skey_group_key, skey_subgroup_key, skey_description_key,
                                     spindle_skey, orientation, flow_arrow, dimensioned, tracing, insulation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (spindle.name, spindle.group_key, spindle.subgroup_key, spindle.description_key,
                  spindle_skey, spindle.orientation, spindle.flow_arrow, spindle.dimensioned,
                  spindle.tracing, spindle.insulation))
            spindle_id = cur.lastrowid

            cur.execute("INSERT INTO spindle_transactions (spindle_id, user, action, comment) VALUES (?, ?, ?, ?)",
                       (spindle_id, user, "create", comment))
            transaction_id = cur.lastrowid

            for geom in spindle.geometry:
                cur.execute("INSERT INTO spindle_geometry (spindle_id, type, data, transaction_id) VALUES (?, ?, ?, ?)",
                           (spindle_id, geom.split(":")[0], geom, transaction_id))
            return spindle_id if spindle_id is not None else 0

    def update_spindle(self, spindle: SkeyData, user: str = "system", comment: str = "edit"):
        """Updates spindle data or creates a new one if it does not exist."""
        sp_skey = spindle.spindle_skey or None  # '' → NULL
        with self._transaction() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM spindles WHERE name = ?", (spindle.name,))
            row = cur.fetchone()
            if not row:
                return self.insert_spindle(spindle, user, comment)

            spindle_id = row[0]
            cur.execute("""
                UPDATE spindles SET skey_group_key = ?, skey_subgroup_key = ?, skey_description_key = ?,
                                   spindle_skey = ?, orientation = ?, flow_arrow = ?, dimensioned = ?,
                                   tracing = ?, insulation = ?
                WHERE id = ?
            """, (spindle.group_key, spindle.subgroup_key, spindle.description_key,
                  sp_skey, spindle.orientation, spindle.flow_arrow, spindle.dimensioned,
                  spindle.tracing, spindle.insulation, spindle_id))

            cur.execute("INSERT INTO spindle_transactions (spindle_id, user, action, comment) VALUES (?, ?, ?, ?)",
                       (spindle_id, user, "edit", comment))
            transaction_id = cur.lastrowid

            for geom in spindle.geometry:
                cur.execute("INSERT INTO spindle_geometry (spindle_id, type, data, transaction_id) VALUES (?, ?, ?, ?)",
                           (spindle_id, geom.split(":")[0], geom, transaction_id))
            return spindle_id

    def _init_spindles_table(self, conn):
        """Creates spindle tables with the new schema (similar to skeys)."""
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS spindles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            skey_group_key TEXT NOT NULL,
            skey_subgroup_key TEXT NOT NULL,
            skey_description_key TEXT,
            spindle_skey TEXT,
            orientation INTEGER NOT NULL DEFAULT 0,
            flow_arrow INTEGER NOT NULL DEFAULT 0,
            dimensioned INTEGER NOT NULL DEFAULT 0,
            tracing INTEGER NOT NULL DEFAULT 0,
            insulation INTEGER NOT NULL DEFAULT 0,
            CHECK (orientation IN (0, 1, 2, 3)),
            CHECK (flow_arrow IN (0, 1, 2)),
            CHECK (dimensioned IN (0, 1, 2)),
            CHECK (tracing IN (0, 1, 2)),
            CHECK (insulation IN (0, 1, 2)),
            FOREIGN KEY (skey_group_key) REFERENCES skey_groups(skey_group_key) ON DELETE RESTRICT ON UPDATE CASCADE,
            FOREIGN KEY (skey_group_key, skey_subgroup_key) REFERENCES skey_subgroups(skey_group_key, skey_subgroup_key) ON DELETE RESTRICT ON UPDATE CASCADE
        )''')

        cur.execute('''CREATE TABLE IF NOT EXISTS spindle_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spindle_id INTEGER NOT NULL,
            user TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            comment TEXT,
            FOREIGN KEY (spindle_id) REFERENCES spindles(id)
        )''')

        cur.execute('''CREATE TABLE IF NOT EXISTS spindle_geometry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spindle_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            data TEXT NOT NULL,
            transaction_id INTEGER NOT NULL,
            FOREIGN KEY (spindle_id) REFERENCES spindles(id),
            FOREIGN KEY (transaction_id) REFERENCES spindle_transactions(id)
        )''')
        conn.commit()

    def get_all_groups(self) -> List[str]:
        """Returns all group keys from the database."""
        with self._transaction(commit=False) as conn:
            cur = conn.cursor()
            try:
                cur.execute("SELECT skey_group_key FROM skey_groups ORDER BY skey_group_key")
                return [row[0] for row in cur.fetchall()]
            except sqlite3.OperationalError:
                return []

    def get_subgroups_by_group(self, group_key: str) -> List[str]:
        """Returns all subgroup keys for the specified group."""
        with self._transaction(commit=False) as conn:
            cur = conn.cursor()
            try:
                cur.execute("""
                    SELECT s.skey_subgroup_key
                    FROM skey_subgroups s
                    JOIN skey_groups g ON s.group_id = g.id
                    WHERE g.skey_group_key = ?
                    ORDER BY s.skey_subgroup_key
                """, (group_key,))
                return [row[0] for row in cur.fetchall()]
            except sqlite3.OperationalError:
                return []

    def ensure_group_exists(self, group_key: str):
        """Ensures that a group key exists in the skey_groups table."""
        with self._transaction() as conn:
            cur = conn.cursor()
            cur.execute("INSERT OR IGNORE INTO skey_groups (skey_group_key) VALUES (?)", (group_key,))

    def ensure_subgroup_exists(self, group_key: str, subgroup_key: str):
        """Ensures that a subgroup key exists in skey_subgroups for the given group."""
        self.ensure_group_exists(group_key)
        with self._transaction() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM skey_groups WHERE skey_group_key = ?", (group_key,))
            group_id = cur.fetchone()[0]
            cur.execute("INSERT OR IGNORE INTO skey_subgroups (group_id, skey_group_key, skey_subgroup_key) VALUES (?, ?, ?)", (group_id, group_key, subgroup_key))
