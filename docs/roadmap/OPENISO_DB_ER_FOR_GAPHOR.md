# ER-схема OpenIso для переноса в Gaphor

Источник: `data/database/openiso.db`
Дата фиксации: 2026-04-22

## Как использовать в Gaphor

1. Создайте UML Diagram.
2. Для каждой таблицы ниже создайте Class с именем таблицы и стереотипом `<<table>>`.
3. Добавьте атрибуты (тип + пометки PK/FK/UNIQUE/NOT NULL).
4. Добавьте ассоциации по разделу «Связи (кардинальности)».

## Сущности (таблицы)

### app_metadata
- key: TEXT, PK
- value: TEXT, NOT NULL

### catalog_symbols
- release_version: TEXT, PK (composite)
- symbol_code: TEXT, PK (composite)
- symbol_version: INTEGER, NOT NULL
- payload_hash: TEXT, NOT NULL
- payload_json: TEXT, NOT NULL

### symbol_sources
- id: INTEGER, PK
- name: TEXT, NOT NULL
- source_type: TEXT, NOT NULL, DEFAULT 'standard'
- version: TEXT, NULL
- description: TEXT, NULL
- url: TEXT, NULL
- UNIQUE(name, source_type, version)

### skey_groups
- id: INTEGER, PK
- skey_group_key: TEXT, NOT NULL, UNIQUE

### skey_subgroups
- id: INTEGER, PK
- group_id: INTEGER, NOT NULL, FK -> skey_groups.id
- skey_group_key: TEXT, NOT NULL, FK -> skey_groups.skey_group_key
- skey_subgroup_key: TEXT, NOT NULL
- UNIQUE(group_id, skey_subgroup_key)
- UNIQUE(skey_group_key, skey_subgroup_key)

### spindles
- id: INTEGER, PK
- name: TEXT, NOT NULL, UNIQUE
- skey_group_key: TEXT, NOT NULL, FK -> skey_groups.skey_group_key
- skey_subgroup_key: TEXT, NOT NULL, FK (composite) -> skey_subgroups.(skey_group_key, skey_subgroup_key)
- skey_description_key: TEXT, NULL
- spindle_skey: TEXT, NULL
- orientation: INTEGER, NOT NULL, DEFAULT 0
- flow_arrow: INTEGER, NOT NULL, DEFAULT 0
- dimensioned: INTEGER, NOT NULL, DEFAULT 0
- tracing: INTEGER, NOT NULL, DEFAULT 0
- insulation: INTEGER, NOT NULL, DEFAULT 0
- source_id: INTEGER, NULL, FK -> symbol_sources.id (ON DELETE SET NULL)
- isogen_standard: INTEGER, NOT NULL, DEFAULT 0

### spindle_transactions
- id: INTEGER, PK
- spindle_id: INTEGER, NOT NULL, FK -> spindles.id
- user: TEXT, NOT NULL
- action: TEXT, NOT NULL
- timestamp: DATETIME, DEFAULT CURRENT_TIMESTAMP
- comment: TEXT, NULL

### spindle_geometry
- id: INTEGER, PK
- spindle_id: INTEGER, NOT NULL, FK -> spindles.id
- type: TEXT, NOT NULL
- data: TEXT, NOT NULL
- transaction_id: INTEGER, NOT NULL, FK -> spindle_transactions.id

### skeys
- id: INTEGER, PK
- name: TEXT, NOT NULL, UNIQUE
- skey_group_key: TEXT, NOT NULL, FK -> skey_groups.skey_group_key
- skey_subgroup_key: TEXT, NOT NULL, FK (composite) -> skey_subgroups.(skey_group_key, skey_subgroup_key)
- skey_description_key: TEXT, NULL
- spindle_skey: TEXT, NULL, FK -> spindles.name (ON DELETE SET NULL, ON UPDATE CASCADE)
- orientation: INTEGER, NOT NULL, DEFAULT 0
- flow_arrow: INTEGER, NOT NULL, DEFAULT 0
- dimensioned: INTEGER, NOT NULL, DEFAULT 0
- tracing: INTEGER, NOT NULL, DEFAULT 0
- insulation: INTEGER, NOT NULL, DEFAULT 0
- pcf_identification: TEXT, NULL
- idf_record: TEXT, NULL
- user_definable: INTEGER, NOT NULL, DEFAULT 1
- flow_dependency: INTEGER, NOT NULL, DEFAULT 0
- source_id: INTEGER, NULL, FK -> symbol_sources.id (ON DELETE SET NULL)
- isogen_standard: INTEGER, NOT NULL, DEFAULT 0
- origin_type: TEXT, NOT NULL, DEFAULT 'official'
- is_official: INTEGER, NOT NULL, DEFAULT 1
- is_user_modified: INTEGER, NOT NULL, DEFAULT 0
- upstream_symbol_code: TEXT, NULL
- upstream_release_version: TEXT, NULL
- upstream_symbol_version: INTEGER, NOT NULL, DEFAULT 1
- last_synced_upstream_version: INTEGER, NOT NULL, DEFAULT 1
- upstream_payload_hash: TEXT, NULL
- local_revision: INTEGER, NOT NULL, DEFAULT 1
- sync_state: TEXT, NOT NULL, DEFAULT 'synced'

### transactions
- id: INTEGER, PK
- skey_id: INTEGER, NOT NULL, FK -> skeys.id
- user: TEXT, NOT NULL
- action: TEXT, NOT NULL
- timestamp: DATETIME, DEFAULT CURRENT_TIMESTAMP
- comment: TEXT, NULL

### geometry
- id: INTEGER, PK
- skey_id: INTEGER, NOT NULL, FK -> skeys.id
- type: TEXT, NOT NULL
- data: TEXT, NOT NULL
- transaction_id: INTEGER, NOT NULL, FK -> transactions.id

## Связи (кардинальности)

- skey_groups (1) -> (N) skey_subgroups
- skey_groups (1) -> (N) skeys
- skey_groups (1) -> (N) spindles

- skey_subgroups (1) -> (N) skeys
- skey_subgroups (1) -> (N) spindles

- symbol_sources (1) -> (N) skeys
- symbol_sources (1) -> (N) spindles

- spindles (1) -> (N) spindle_transactions
- spindles (1) -> (N) spindle_geometry
- spindle_transactions (1) -> (N) spindle_geometry

- spindles (1) -> (N) skeys, связь по `spindles.name = skeys.spindle_skey`

- skeys (1) -> (N) transactions
- skeys (1) -> (N) geometry
- transactions (1) -> (N) geometry

## Индексы (учесть как notes/constraints в диаграмме)

- idx_transactions_skey on transactions(skey_id)
- idx_geometry_skey_txn on geometry(skey_id, transaction_id)
- idx_spindle_geometry_spindle_txn on spindle_geometry(spindle_id, transaction_id)

## Рекомендуемая группировка блоков на диаграмме

- Справочники: symbol_sources, skey_groups, skey_subgroups
- Основные сущности: skeys, spindles
- История skey: transactions, geometry
- История spindle: spindle_transactions, spindle_geometry
- Каталог/служебное: catalog_symbols, app_metadata
