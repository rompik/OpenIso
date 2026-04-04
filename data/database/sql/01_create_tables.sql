-- Create tables for storing Skey data and change history

CREATE TABLE IF NOT EXISTS skeys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    skey_group_key TEXT NOT NULL,
    skey_subgroup_key TEXT NOT NULL,
    skey_description_key TEXT,
    spindle_skey TEXT,                                       -- nullable FK → spindles(name)
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
    FOREIGN KEY (skey_group_key, skey_subgroup_key) REFERENCES skey_subgroups(skey_group_key, skey_subgroup_key) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (spindle_skey) REFERENCES spindles(name) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skey_id INTEGER NOT NULL,
    user TEXT NOT NULL,
    action TEXT NOT NULL, -- create, edit, delete
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    comment TEXT,
    FOREIGN KEY (skey_id) REFERENCES skeys(id)
);

CREATE TABLE IF NOT EXISTS geometry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skey_id INTEGER NOT NULL,
    type TEXT NOT NULL, -- ArrivePoint, LeavePoint, Line, Rectangle, Polygon, etc.
    data TEXT NOT NULL, -- serialized parameters (e.g. JSON or a plain string)
    transaction_id INTEGER NOT NULL,
    FOREIGN KEY (skey_id) REFERENCES skeys(id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
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

-- Indexes to speed up geometry and transaction queries
CREATE INDEX IF NOT EXISTS idx_geometry_skey_txn ON geometry(skey_id, transaction_id);
CREATE INDEX IF NOT EXISTS idx_transactions_skey ON transactions(skey_id);
CREATE INDEX IF NOT EXISTS idx_spindle_geometry_spindle_txn ON spindle_geometry(spindle_id, transaction_id);
