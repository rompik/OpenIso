# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import os
import shutil
import sqlite3
from pathlib import Path
from typing import List

from openiso.model.skey import SkeyData

DB_PATH = "data/database/openiso.db"

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
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='skeys'")
        has_skeys = cur.fetchone() is not None
        if has_skeys:
            conn.close()
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
                pcf_identification TEXT,
                idf_record TEXT,
                user_definable INTEGER NOT NULL DEFAULT 1,
                flow_dependency INTEGER NOT NULL DEFAULT 0,
                source_id INTEGER,
                isogen_standard INTEGER NOT NULL DEFAULT 0,
                CHECK (orientation IN (0, 1, 2, 3)),
                CHECK (flow_arrow IN (0, 1, 2)),
                CHECK (dimensioned IN (0, 1, 2)),
                CHECK (tracing IN (0, 1, 2)),
                CHECK (insulation IN (0, 1, 2)),
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

            CREATE INDEX IF NOT EXISTS idx_geometry_skey_txn ON geometry(skey_id, transaction_id);
            CREATE INDEX IF NOT EXISTS idx_transactions_skey ON transactions(skey_id);
            CREATE INDEX IF NOT EXISTS idx_spindle_geometry_spindle_txn ON spindle_geometry(spindle_id, transaction_id);
            """
        )
        conn.commit()
        conn.close()

    @staticmethod
    def _column_exists(cur: sqlite3.Cursor, table: str, column: str) -> bool:
        cur.execute(f"PRAGMA table_info({table})")
        return any(row[1] == column for row in cur.fetchall())

    def _ensure_columns_exist(self):
        """Checks if all necessary columns exist and adds them if missing."""
        conn = self.connect()
        cur = conn.cursor()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='skeys'")
        if cur.fetchone() is None:
            conn.close()
            return

        try:
            cur.execute("SELECT tracing FROM skeys LIMIT 1")
        except sqlite3.OperationalError:
            print("Adding 'tracing' column to 'skeys' table...")
            try:
                cur.execute("ALTER TABLE skeys ADD COLUMN tracing INTEGER DEFAULT 0")
                conn.commit()
            except Exception as e:
                print(f"Failed to add 'tracing' column: {e}")

        try:
            cur.execute("SELECT insulation FROM skeys LIMIT 1")
        except sqlite3.OperationalError:
            print("Adding 'insulation' column to 'skeys' table...")
            try:
                cur.execute("ALTER TABLE skeys ADD COLUMN insulation INTEGER DEFAULT 0")
                conn.commit()
            except Exception as e:
                print(f"Failed to add 'insulation' column: {e}")

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
        conn.commit()
        conn.close()

    def _ensure_symbol_source(self, name: str, source_type: str = "standard", version: str = "") -> int | None:
        source_name = (name or "").strip()
        if not source_name:
            return None

        source_type = (source_type or "standard").strip().lower()
        if source_type not in ("standard", "company", "project"):
            source_type = "standard"

        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM symbol_sources WHERE name = ? AND source_type = ? AND COALESCE(version, '') = COALESCE(?, '')",
            (source_name, source_type, version),
        )
        row = cur.fetchone()
        if row:
            conn.close()
            return row[0]

        cur.execute(
            "INSERT INTO symbol_sources (name, source_type, version) VALUES (?, ?, ?)",
            (source_name, source_type, version),
        )
        source_id = cur.lastrowid
        conn.commit()
        conn.close()
        return source_id if source_id is not None else None

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def get_all_skeys(self) -> List[SkeyData]:
        conn = self.connect()
        cur = conn.cursor()
        has_tracing = self._column_exists(cur, "skeys", "tracing")
        has_insulation = self._column_exists(cur, "skeys", "insulation")
        has_pcf = self._column_exists(cur, "skeys", "pcf_identification")
        has_idf = self._column_exists(cur, "skeys", "idf_record")
        has_user_definable = self._column_exists(cur, "skeys", "user_definable")
        has_flow_dependency = self._column_exists(cur, "skeys", "flow_dependency")
        has_source_id = self._column_exists(cur, "skeys", "source_id")
        has_isogen_standard = self._column_exists(cur, "skeys", "isogen_standard")

        select_columns = [
            "s.id", "s.name", "s.skey_group_key", "s.skey_subgroup_key", "s.skey_description_key",
            "s.spindle_skey", "s.orientation", "s.flow_arrow", "s.dimensioned",
        ]
        if has_tracing:
            select_columns.append("s.tracing")
        if has_insulation:
            select_columns.append("s.insulation")
        if has_pcf:
            select_columns.append("s.pcf_identification")
        if has_idf:
            select_columns.append("s.idf_record")
        if has_user_definable:
            select_columns.append("s.user_definable")
        if has_flow_dependency:
            select_columns.append("s.flow_dependency")
        if has_source_id:
            select_columns.extend(["s.source_id", "ss.name", "ss.source_type", "ss.version"])
        if has_isogen_standard:
            select_columns.append("s.isogen_standard")

        query = f"SELECT {', '.join(select_columns)} FROM skeys s"
        if has_source_id:
            query += " LEFT JOIN symbol_sources ss ON ss.id = s.source_id"
        query += " ORDER BY s.name"
        cur.execute(query)

        rows = cur.fetchall()
        skeys = []
        for row in rows:
            idx = 0
            skey_id = row[idx]; idx += 1
            name = row[idx]; idx += 1
            skey_group_key = row[idx]; idx += 1
            skey_subgroup_key = row[idx]; idx += 1
            skey_description_key = row[idx]; idx += 1
            spindle_skey = row[idx]; idx += 1
            orientation = row[idx]; idx += 1
            flow_arrow = row[idx]; idx += 1
            dimensioned = row[idx]; idx += 1

            tracing = row[idx] if has_tracing else 0
            if has_tracing:
                idx += 1
            insulation = row[idx] if has_insulation else 0
            if has_insulation:
                idx += 1

            pcf_identification = row[idx] if has_pcf else ""
            if has_pcf:
                idx += 1
            idf_record = row[idx] if has_idf else ""
            if has_idf:
                idx += 1
            user_definable = row[idx] if has_user_definable else 1
            if has_user_definable:
                idx += 1
            flow_dependency = row[idx] if has_flow_dependency else 0
            if has_flow_dependency:
                idx += 1

            source_id = row[idx] if has_source_id else None
            source_name = ""
            source_type = "standard"
            source_version = ""
            if has_source_id:
                idx += 1
                source_name = row[idx] or ""
                idx += 1
                source_type = row[idx] or "standard"
                idx += 1
                source_version = row[idx] or ""
                idx += 1

            isogen_standard = row[idx] if has_isogen_standard else 0

            geometry = self.get_latest_geometry_for_skey(skey_id)
            skeys.append(SkeyData(
                name=name,
                group_key=skey_group_key,
                subgroup_key=skey_subgroup_key,
                description_key=skey_description_key,
                spindle_skey=spindle_skey or "",  # NULL -> '' for the model
                orientation=orientation,
                flow_arrow=flow_arrow,
                dimensioned=dimensioned,
                tracing=tracing,
                insulation=insulation,
                pcf_identification=pcf_identification or "",
                idf_record=idf_record or "",
                user_definable=user_definable,
                flow_dependency=flow_dependency,
                source_id=source_id,
                source_name=source_name,
                source_type=source_type,
                source_version=source_version,
                isogen_standard=isogen_standard,
                geometry=geometry
            ))
        conn.close()
        return skeys

    def get_latest_geometry_for_skey(self, skey_id: int) -> List[str]:
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT MAX(transaction_id) FROM geometry WHERE skey_id = ?", (skey_id,))
        row = cur.fetchone()
        if not row or row[0] is None:
            conn.close()
            return []
        transaction_id = row[0]
        cur.execute("SELECT data FROM geometry WHERE skey_id = ? AND transaction_id = ? ORDER BY id ASC", (skey_id, transaction_id))
        geometry = [r[0] for r in cur.fetchall()]
        conn.close()
        return geometry

    def insert_skey(self, skey: SkeyData, user: str = "system", comment: str = "create") -> int:
        conn = self.connect()
        cur = conn.cursor()
        spindle_skey = skey.spindle_skey or None  # '' -> NULL for proper FK behavior
        source_id = skey.source_id if skey.source_id is not None else self._ensure_symbol_source(
            skey.source_name, skey.source_type, skey.source_version
        )
        cur.execute(
            """
            INSERT INTO skeys (
                name, skey_group_key, skey_subgroup_key, skey_description_key,
                spindle_skey, orientation, flow_arrow, dimensioned, tracing, insulation,
                pcf_identification, idf_record, user_definable, flow_dependency,
                source_id, isogen_standard
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                skey.name, skey.group_key, skey.subgroup_key, skey.description_key,
                spindle_skey, skey.orientation, skey.flow_arrow, skey.dimensioned,
                skey.tracing, skey.insulation,
                skey.pcf_identification, skey.idf_record, skey.user_definable,
                skey.flow_dependency, source_id, skey.isogen_standard,
            ),
        )
        skey_id = cur.lastrowid
        cur.execute("INSERT INTO transactions (skey_id, user, action, comment) VALUES (?, ?, ?, ?)", (skey_id, user, "create", comment))
        transaction_id = cur.lastrowid
        for geom in skey.geometry:
            cur.execute("INSERT INTO geometry (skey_id, type, data, transaction_id) VALUES (?, ?, ?, ?)", (skey_id, geom.split(":")[0], geom, transaction_id))
        conn.commit()
        conn.close()
        return skey_id if skey_id is not None else 0

    def delete_skey(self, skey_name: str):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT id FROM skeys WHERE name = ?", (skey_name,))
        row = cur.fetchone()
        if row:
            skey_id = row[0]
            cur.execute("DELETE FROM geometry WHERE skey_id = ?", (skey_id,))
            cur.execute("DELETE FROM transactions WHERE skey_id = ?", (skey_id,))
            cur.execute("DELETE FROM skeys WHERE id = ?", (skey_id,))
            conn.commit()
        conn.close()

    def update_skey(self, skey: SkeyData, user: str = "system", comment: str = "edit"):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT id FROM skeys WHERE name = ?", (skey.name,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return self.insert_skey(skey, user, comment)
        skey_id = row[0]
        spindle_skey = skey.spindle_skey or None  # '' → NULL
        source_id = skey.source_id if skey.source_id is not None else self._ensure_symbol_source(
            skey.source_name, skey.source_type, skey.source_version
        )
        cur.execute(
            """
            UPDATE skeys SET
                skey_group_key = ?,
                skey_subgroup_key = ?,
                skey_description_key = ?,
                spindle_skey = ?,
                orientation = ?,
                flow_arrow = ?,
                dimensioned = ?,
                tracing = ?,
                insulation = ?,
                pcf_identification = ?,
                idf_record = ?,
                user_definable = ?,
                flow_dependency = ?,
                source_id = ?,
                isogen_standard = ?
            WHERE id = ?
            """,
            (
                skey.group_key, skey.subgroup_key, skey.description_key,
                spindle_skey, skey.orientation, skey.flow_arrow, skey.dimensioned,
                skey.tracing, skey.insulation,
                skey.pcf_identification, skey.idf_record, skey.user_definable,
                skey.flow_dependency, source_id, skey.isogen_standard,
                skey_id,
            ),
        )
        cur.execute("INSERT INTO transactions (skey_id, user, action, comment) VALUES (?, ?, ?, ?)", (skey_id, user, "edit", comment))
        transaction_id = cur.lastrowid
        for geom in skey.geometry:
            cur.execute("INSERT INTO geometry (skey_id, type, data, transaction_id) VALUES (?, ?, ?, ?)", (skey_id, geom.split(":")[0], geom, transaction_id))
        conn.commit()
        conn.close()
        return skey_id if skey_id is not None else 0

    def get_spindle_geometry(self, spindle_name: str) -> List[str]:

        conn = self.connect()
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
        finally:
            conn.close()

    def get_all_spindles(self) -> List[SkeyData]:
        """Returns all spindles as SkeyData objects from the database."""
        conn = self.connect()
        cur = conn.cursor()
        spindles = []
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
        finally:
            conn.close()
        return spindles

    def insert_spindle(self, spindle: SkeyData, user: str = "system", comment: str = "create") -> int:
        """Inserts a new spindle into the database (similar to Skey)."""
        conn = self.connect()
        cur = conn.cursor()
        spindle_skey = spindle.spindle_skey or None  # '' → NULL
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
        conn.commit()
        conn.close()
        return spindle_id if spindle_id is not None else 0

    def update_spindle(self, spindle: SkeyData, user: str = "system", comment: str = "edit"):
        """Updates spindle data or creates a new one if it does not exist."""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT id FROM spindles WHERE name = ?", (spindle.name,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return self.insert_spindle(spindle, user, comment)

        spindle_id = row[0]
        sp_skey = spindle.spindle_skey or None  # '' → NULL
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
        conn.commit()
        conn.close()
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
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT skey_group_key FROM skey_groups ORDER BY skey_group_key")
            return [row[0] for row in cur.fetchall()]
        except sqlite3.OperationalError:
            return []
        finally:
            conn.close()

    def get_subgroups_by_group(self, group_key: str) -> List[str]:
        """Returns all subgroup keys for the specified group."""
        conn = self.connect()
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
        finally:
            conn.close()

    def ensure_group_exists(self, group_key: str):
        """Ensures that a group key exists in the skey_groups table."""
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("INSERT OR IGNORE INTO skey_groups (skey_group_key) VALUES (?)", (group_key,))
            conn.commit()
        finally:
            conn.close()

    def ensure_subgroup_exists(self, group_key: str, subgroup_key: str):
        """Ensures that a subgroup key exists in skey_subgroups for the given group."""
        self.ensure_group_exists(group_key)
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT id FROM skey_groups WHERE skey_group_key = ?", (group_key,))
            group_id = cur.fetchone()[0]
            cur.execute("INSERT OR IGNORE INTO skey_subgroups (group_id, skey_group_key, skey_subgroup_key) VALUES (?, ?, ?)", (group_id, group_key, subgroup_key))
            conn.commit()
        finally:
            conn.close()
