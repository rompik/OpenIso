import sqlite3
from typing import List
from openiso.model.skey import SkeyData

DB_PATH = "data/database/openiso.db"

class SkeyDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_columns_exist()

    def _ensure_columns_exist(self):
        """Checks if all necessary columns exist and adds them if missing."""
        conn = self.connect()
        cur = conn.cursor()
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
        finally:
            conn.close()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def get_all_skeys(self) -> List[SkeyData]:
        conn = self.connect()
        cur = conn.cursor()
        # Try to include columns if they exist
        try:
            cur.execute("SELECT id, name, skey_group_key, skey_subgroup_key, skey_description_key, spindle_skey, orientation, flow_arrow, dimensioned, tracing, insulation FROM skeys")
        except sqlite3.OperationalError:
            try:
                cur.execute("SELECT id, name, skey_group_key, skey_subgroup_key, skey_description_key, spindle_skey, orientation, flow_arrow, dimensioned, tracing FROM skeys")
            except sqlite3.OperationalError:
                cur.execute("SELECT id, name, skey_group_key, skey_subgroup_key, skey_description_key, spindle_skey, orientation, flow_arrow, dimensioned FROM skeys")

        rows = cur.fetchall()
        skeys = []
        for row in rows:
            tracing = 0
            insulation = 0
            if len(row) == 11:
                skey_id, name, skey_group_key, skey_subgroup_key, skey_description_key, spindle_skey, orientation, flow_arrow, dimensioned, tracing, insulation = row
            elif len(row) == 10:
                skey_id, name, skey_group_key, skey_subgroup_key, skey_description_key, spindle_skey, orientation, flow_arrow, dimensioned, tracing = row
            else:
                skey_id, name, skey_group_key, skey_subgroup_key, skey_description_key, spindle_skey, orientation, flow_arrow, dimensioned = row

            geometry = self.get_latest_geometry_for_skey(skey_id)
            skeys.append(SkeyData(
                name=name,
                group_key=skey_group_key,
                subgroup_key=skey_subgroup_key,
                description_key=skey_description_key,
                spindle_skey=spindle_skey,
                orientation=orientation,
                flow_arrow=flow_arrow,
                dimensioned=dimensioned,
                tracing=tracing,
                insulation=insulation,
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
        cur.execute("INSERT INTO skeys (name, skey_group_key, skey_subgroup_key, skey_description_key, spindle_skey, orientation, flow_arrow, dimensioned, tracing, insulation) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (skey.name, skey.group_key, skey.subgroup_key, skey.description_key, skey.spindle_skey, skey.orientation, skey.flow_arrow, skey.dimensioned, skey.tracing, skey.insulation))
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
        cur.execute("UPDATE skeys SET skey_group_key = ?, skey_subgroup_key = ?, skey_description_key = ?, spindle_skey = ?, orientation = ?, flow_arrow = ?, dimensioned = ?, tracing = ?, insulation = ? WHERE id = ?",
            (skey.group_key, skey.subgroup_key, skey.description_key, skey.spindle_skey, skey.orientation, skey.flow_arrow, skey.dimensioned, skey.tracing, skey.insulation, skey_id))
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
        """Возвращает список всех шпинделей как объекты SkeyData из базы данных."""
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
            # Таблица может отсутствовать или иметь старую структуру
            self._init_spindles_table(conn)
        finally:
            conn.close()
        return spindles

    def insert_spindle(self, spindle: SkeyData, user: str = "system", comment: str = "create") -> int:
        """Вставляет новый шпиндель в базу данных (аналогично Skey)."""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO spindles (name, skey_group_key, skey_subgroup_key, skey_description_key,
                                 spindle_skey, orientation, flow_arrow, dimensioned, tracing, insulation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (spindle.name, spindle.group_key, spindle.subgroup_key, spindle.description_key,
              spindle.spindle_skey, spindle.orientation, spindle.flow_arrow, spindle.dimensioned,
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
        """Обновляет данные шпинделя или создает новый, если его нет."""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT id FROM spindles WHERE name = ?", (spindle.name,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return self.insert_spindle(spindle, user, comment)

        spindle_id = row[0]
        cur.execute("""
            UPDATE spindles SET skey_group_key = ?, skey_subgroup_key = ?, skey_description_key = ?,
                               spindle_skey = ?, orientation = ?, flow_arrow = ?, dimensioned = ?,
                               tracing = ?, insulation = ?
            WHERE id = ?
        """, (spindle.group_key, spindle.subgroup_key, spindle.description_key,
              spindle.spindle_skey, spindle.orientation, spindle.flow_arrow, spindle.dimensioned,
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
        """Создает таблицы для шпинделей с новой структурой (аналогично skeys)."""
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS spindles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            skey_group_key TEXT,
            skey_subgroup_key TEXT,
            skey_description_key TEXT,
            spindle_skey TEXT,
            orientation INTEGER,
            flow_arrow INTEGER,
            dimensioned INTEGER,
            tracing INTEGER,
            insulation INTEGER
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
        """Возвращает список всех ключей групп из базы данных."""
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
        """Возвращает список всех ключей подгрупп для указанной группы."""
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
        """Гарантирует, что ключ группы существует в таблице skey_groups."""
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("INSERT OR IGNORE INTO skey_groups (skey_group_key) VALUES (?)", (group_key,))
            conn.commit()
        finally:
            conn.close()

    def ensure_subgroup_exists(self, group_key: str, subgroup_key: str):
        """Гарантирует, что ключ подгруппы существует в таблице skey_subgroups для данной группы."""
        self.ensure_group_exists(group_key)
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT id FROM skey_groups WHERE skey_group_key = ?", (group_key,))
            group_id = cur.fetchone()[0]
            cur.execute("INSERT OR IGNORE INTO skey_subgroups (group_id, skey_subgroup_key) VALUES (?, ?)", (group_id, subgroup_key))
            conn.commit()
        finally:
            conn.close()
