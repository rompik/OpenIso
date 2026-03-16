-- Таблица шпинделей
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
    CHECK (orientation IN (0, 1, 2, 3)),
    CHECK (flow_arrow IN (0, 1, 2)),
    CHECK (dimensioned IN (0, 1, 2)),
    CHECK (tracing IN (0, 1, 2)),
    CHECK (insulation IN (0, 1, 2)),
    FOREIGN KEY (skey_group_key) REFERENCES skey_groups(skey_group_key) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (skey_group_key, skey_subgroup_key) REFERENCES skey_subgroups(skey_group_key, skey_subgroup_key) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Таблица транзакций для шпинделей
CREATE TABLE IF NOT EXISTS spindle_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spindle_id INTEGER NOT NULL,
    user TEXT NOT NULL,
    action TEXT NOT NULL, -- create, edit, delete
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    comment TEXT,
    FOREIGN KEY (spindle_id) REFERENCES spindles(id)
);

-- Таблица геометрии шпинделей
CREATE TABLE IF NOT EXISTS spindle_geometry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spindle_id INTEGER NOT NULL,
    type TEXT NOT NULL, -- тип элемента (например, Line, Point, Polygon и т.д.)
    data TEXT NOT NULL, -- сериализованные параметры (например, JSON или строка)
    transaction_id INTEGER NOT NULL,
    FOREIGN KEY (spindle_id) REFERENCES spindles(id),
    FOREIGN KEY (transaction_id) REFERENCES spindle_transactions(id)
);
