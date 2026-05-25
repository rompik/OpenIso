# OpenIso DB: UML-модель для Gaphor

Источник: `data/database/openiso.db`
Формат: готово для ручного переноса в UML Class Diagram в Gaphor

## 1) Классы (таблицы)

Стереотип для каждого класса: `<<table>>`

### app_metadata
Атрибуты:
- key: TEXT {PK}
- value: TEXT {NOT NULL}

### catalog_symbols
Атрибуты:
- release_version: TEXT {PK part}
- symbol_code: TEXT {PK part}
- symbol_version: INTEGER {NOT NULL}
- payload_hash: TEXT {NOT NULL}
- payload_json: TEXT {NOT NULL}

### symbol_sources
Атрибуты:
- id: INTEGER {PK}
- name: TEXT {NOT NULL}
- source_type: TEXT {NOT NULL, default='standard'}
- version: TEXT
- description: TEXT
- url: TEXT

Ограничения:
- unique(name, source_type, version)

### skey_groups
Атрибуты:
- id: INTEGER {PK}
- skey_group_key: TEXT {NOT NULL, UNIQUE}

### skey_subgroups
Атрибуты:
- id: INTEGER {PK}
- group_id: INTEGER {NOT NULL, FK -> skey_groups.id}
- skey_group_key: TEXT {NOT NULL, FK -> skey_groups.skey_group_key}
- skey_subgroup_key: TEXT {NOT NULL}

Ограничения:
- unique(group_id, skey_subgroup_key)
- unique(skey_group_key, skey_subgroup_key)

### spindles
Атрибуты:
- id: INTEGER {PK}
- name: TEXT {NOT NULL, UNIQUE}
- skey_group_key: TEXT {NOT NULL, FK -> skey_groups.skey_group_key}
- skey_subgroup_key: TEXT {NOT NULL, FK -> skey_subgroups.(skey_group_key,skey_subgroup_key)}
- skey_description_key: TEXT
- spindle_skey: TEXT
- orientation: INTEGER {NOT NULL, default=0}
- flow_arrow: INTEGER {NOT NULL, default=0}
- dimensioned: INTEGER {NOT NULL, default=0}
- tracing: INTEGER {NOT NULL, default=0}
- insulation: INTEGER {NOT NULL, default=0}
- source_id: INTEGER {FK -> symbol_sources.id, onDelete=SET NULL}
- isogen_standard: INTEGER {NOT NULL, default=0}

### spindle_transactions
Атрибуты:
- id: INTEGER {PK}
- spindle_id: INTEGER {NOT NULL, FK -> spindles.id}
- user: TEXT {NOT NULL}
- action: TEXT {NOT NULL}
- timestamp: DATETIME {default=CURRENT_TIMESTAMP}
- comment: TEXT

### spindle_geometry
Атрибуты:
- id: INTEGER {PK}
- spindle_id: INTEGER {NOT NULL, FK -> spindles.id}
- type: TEXT {NOT NULL}
- data: TEXT {NOT NULL}
- transaction_id: INTEGER {NOT NULL, FK -> spindle_transactions.id}

### skeys
Атрибуты:
- id: INTEGER {PK}
- name: TEXT {NOT NULL, UNIQUE}
- skey_group_key: TEXT {NOT NULL, FK -> skey_groups.skey_group_key}
- skey_subgroup_key: TEXT {NOT NULL, FK -> skey_subgroups.(skey_group_key,skey_subgroup_key)}
- skey_description_key: TEXT
- spindle_skey: TEXT {FK -> spindles.name, onDelete=SET NULL, onUpdate=CASCADE}
- orientation: INTEGER {NOT NULL, default=0}
- flow_arrow: INTEGER {NOT NULL, default=0}
- dimensioned: INTEGER {NOT NULL, default=0}
- tracing: INTEGER {NOT NULL, default=0}
- insulation: INTEGER {NOT NULL, default=0}
- pcf_identification: TEXT
- idf_record: TEXT
- user_definable: INTEGER {NOT NULL, default=1}
- flow_dependency: INTEGER {NOT NULL, default=0}
- source_id: INTEGER {FK -> symbol_sources.id, onDelete=SET NULL}
- isogen_standard: INTEGER {NOT NULL, default=0}
- origin_type: TEXT {NOT NULL, default='official'}
- is_official: INTEGER {NOT NULL, default=1}
- is_user_modified: INTEGER {NOT NULL, default=0}
- upstream_symbol_code: TEXT
- upstream_release_version: TEXT
- upstream_symbol_version: INTEGER {NOT NULL, default=1}
- last_synced_upstream_version: INTEGER {NOT NULL, default=1}
- upstream_payload_hash: TEXT
- local_revision: INTEGER {NOT NULL, default=1}
- sync_state: TEXT {NOT NULL, default='synced'}

### transactions
Атрибуты:
- id: INTEGER {PK}
- skey_id: INTEGER {NOT NULL, FK -> skeys.id}
- user: TEXT {NOT NULL}
- action: TEXT {NOT NULL}
- timestamp: DATETIME {default=CURRENT_TIMESTAMP}
- comment: TEXT

### geometry
Атрибуты:
- id: INTEGER {PK}
- skey_id: INTEGER {NOT NULL, FK -> skeys.id}
- type: TEXT {NOT NULL}
- data: TEXT {NOT NULL}
- transaction_id: INTEGER {NOT NULL, FK -> transactions.id}

## 2) Ассоциации (для Gaphor)

Ниже формат:
`Источник(кратность) -- роль/имя_связи -- (кратность)Приемник`

- skey_groups(1) -- has_subgroups -- (0..*)skey_subgroups
- skey_groups(1) -- has_skeys -- (0..*)skeys
- skey_groups(1) -- has_spindles -- (0..*)spindles

- skey_subgroups(1) -- contains_skeys -- (0..*)skeys
- skey_subgroups(1) -- contains_spindles -- (0..*)spindles

- symbol_sources(1) -- sources_skeys -- (0..*)skeys
- symbol_sources(1) -- sources_spindles -- (0..*)spindles

- spindles(1) -- has_transactions -- (0..*)spindle_transactions
- spindles(1) -- has_geometry -- (0..*)spindle_geometry
- spindle_transactions(1) -- writes_geometry -- (0..*)spindle_geometry

- spindles(1) -- linked_as_spindle_skey_by_name -- (0..*)skeys
  note: связь по `spindles.name = skeys.spindle_skey`

- skeys(1) -- has_transactions -- (0..*)transactions
- skeys(1) -- has_geometry -- (0..*)geometry
- transactions(1) -- writes_geometry -- (0..*)geometry

## 3) Визуальная раскладка (рекомендуется)

- Слева: `skey_groups`, `skey_subgroups`, `symbol_sources`
- Центр: `skeys`, `spindles`
- Справа сверху: `transactions`, `geometry`
- Справа снизу: `spindle_transactions`, `spindle_geometry`
- Отдельно снизу: `catalog_symbols`, `app_metadata`

## 4) Ограничения как Notes в Gaphor

Добавьте `Note` к таблицам:
- `skeys`: CHECK orientation/flow_arrow/dimensioned/tracing/insulation
- `spindles`: CHECK orientation/flow_arrow/dimensioned/tracing/insulation
- `skey_subgroups`: unique(group_id, skey_subgroup_key), unique(skey_group_key, skey_subgroup_key)
- `symbol_sources`: unique(name, source_type, version)

## 5) Индексы (как Notes)

- idx_transactions_skey: transactions(skey_id)
- idx_geometry_skey_txn: geometry(skey_id, transaction_id)
- idx_spindle_geometry_spindle_txn: spindle_geometry(spindle_id, transaction_id)
