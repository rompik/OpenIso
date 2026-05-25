# ER v2 OpenIso для переноса в Gaphor

Источник: целевая модель данных для Canonical v1
Дата фиксации: 2026-05-16
Статус: draft-ready для переноса в Gaphor

## 1. Назначение

Документ описывает целевую ER-модель v2 для перехода на единый формат данных.

Модель решает задачи:
1. Явное разделение символа, геометрии и коннекторов.
2. Поддержка версионирования upstream/local.
3. Прозрачная история изменений.
4. Безопасная синхронизация официального каталога и локальных правок.

## 2. Инструкция для Gaphor

1. Создать UML Class Diagram.
2. На каждую таблицу ниже создать Class со стереотипом <<table>>.
3. Добавить атрибуты с пометками PK/FK/UNIQUE/NOT NULL.
4. Добавить ассоциации из раздела Связи.
5. Добавить Notes с ограничениями и индексами.

## 3. Сущности v2

### migration_history
- id: INTEGER, PK
- migration_key: TEXT, NOT NULL, UNIQUE
- applied_at: DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP
- checksum: TEXT, NOT NULL
- applied_by: TEXT, NULL

### symbol_sources
- id: INTEGER, PK
- name: TEXT, NOT NULL
- source_type: TEXT, NOT NULL, DEFAULT 'standard'
- version: TEXT, NULL
- description: TEXT, NULL
- url: TEXT, NULL
- UNIQUE(name, source_type, version)

### release_catalogs
- id: INTEGER, PK
- source_id: INTEGER, NOT NULL, FK -> symbol_sources.id
- release_version: TEXT, NOT NULL
- published_at: DATETIME, NULL
- manifest_hash: TEXT, NULL
- UNIQUE(source_id, release_version)

### symbols
- id: INTEGER, PK
- symbol_code: TEXT, NOT NULL, UNIQUE
- name: TEXT, NULL
- group_key: TEXT, NOT NULL
- subgroup_key: TEXT, NOT NULL
- description: TEXT, NULL
- lifecycle_state: TEXT, NOT NULL, DEFAULT 'active'
- source_id: INTEGER, NULL, FK -> symbol_sources.id
- created_at: DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP
- updated_at: DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP
- UNIQUE(group_key, subgroup_key, symbol_code)

### symbol_versions
- id: INTEGER, PK
- symbol_id: INTEGER, NOT NULL, FK -> symbols.id
- release_catalog_id: INTEGER, NULL, FK -> release_catalogs.id
- upstream_symbol_version: INTEGER, NOT NULL, DEFAULT 1
- local_revision: INTEGER, NOT NULL, DEFAULT 1
- payload_hash: TEXT, NOT NULL
- last_synced_upstream_version: INTEGER, NOT NULL, DEFAULT 1
- sync_state: TEXT, NOT NULL, DEFAULT 'synced'
- is_user_modified: INTEGER, NOT NULL, DEFAULT 0
- is_official: INTEGER, NOT NULL, DEFAULT 1
- origin_type: TEXT, NOT NULL, DEFAULT 'official'
- is_current: INTEGER, NOT NULL, DEFAULT 1
- created_at: DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP
- UNIQUE(symbol_id, local_revision)

### symbol_attributes
- id: INTEGER, PK
- symbol_version_id: INTEGER, NOT NULL, FK -> symbol_versions.id
- orientation: INTEGER, NOT NULL, DEFAULT 0
- flow_arrow: INTEGER, NOT NULL, DEFAULT 0
- dimensioned: INTEGER, NOT NULL, DEFAULT 0
- tracing: INTEGER, NOT NULL, DEFAULT 0
- insulation: INTEGER, NOT NULL, DEFAULT 0
- spindle_skey: TEXT, NULL
- pcf_identification: TEXT, NULL
- idf_record: TEXT, NULL
- user_definable: INTEGER, NOT NULL, DEFAULT 1
- flow_dependency: INTEGER, NOT NULL, DEFAULT 0
- UNIQUE(symbol_version_id)

### symbol_connectors
- id: INTEGER, PK
- symbol_version_id: INTEGER, NOT NULL, FK -> symbol_versions.id
- kind: TEXT, NOT NULL
- x: REAL, NOT NULL
- y: REAL, NOT NULL
- direction: TEXT, NULL
- connector_meta: TEXT, NULL
- seq_no: INTEGER, NOT NULL, DEFAULT 1

### symbol_segments
- id: INTEGER, PK
- symbol_version_id: INTEGER, NOT NULL, FK -> symbol_versions.id
- segment_type: TEXT, NOT NULL
- seq_no: INTEGER, NOT NULL
- x1: REAL, NULL
- y1: REAL, NULL
- x2: REAL, NULL
- y2: REAL, NULL
- cx: REAL, NULL
- cy: REAL, NULL
- r: REAL, NULL
- start_angle: REAL, NULL
- end_angle: REAL, NULL
- points_json: TEXT, NULL
- closed: INTEGER, NULL
- rotation: REAL, NULL
- segment_meta: TEXT, NULL
- UNIQUE(symbol_version_id, seq_no)

### sync_conflicts
- id: INTEGER, PK
- symbol_id: INTEGER, NOT NULL, FK -> symbols.id
- local_symbol_version_id: INTEGER, NOT NULL, FK -> symbol_versions.id
- upstream_release_catalog_id: INTEGER, NOT NULL, FK -> release_catalogs.id
- upstream_symbol_version: INTEGER, NOT NULL
- local_payload_hash: TEXT, NOT NULL
- upstream_payload_hash: TEXT, NOT NULL
- status: TEXT, NOT NULL, DEFAULT 'open'
- created_at: DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP
- resolved_at: DATETIME, NULL
- resolution: TEXT, NULL

### symbol_change_log
- id: INTEGER, PK
- symbol_version_id: INTEGER, NOT NULL, FK -> symbol_versions.id
- actor: TEXT, NOT NULL
- action: TEXT, NOT NULL
- comment: TEXT, NULL
- created_at: DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP

## 4. Связи (кардинальности)

1. symbol_sources (1) -> (N) release_catalogs
2. symbol_sources (1) -> (N) symbols
3. release_catalogs (1) -> (N) symbol_versions
4. symbols (1) -> (N) symbol_versions
5. symbol_versions (1) -> (1) symbol_attributes
6. symbol_versions (1) -> (N) symbol_connectors
7. symbol_versions (1) -> (N) symbol_segments
8. symbols (1) -> (N) sync_conflicts
9. symbol_versions (1) -> (N) symbol_change_log
10. symbol_versions (1) -> (N) sync_conflicts (как local_symbol_version_id)

## 5. Ограничения (Notes в Gaphor)

### 5.1 Enum-поля

1. symbol_versions.sync_state in (synced, conflict, upstream_newer, deprecated_upstream)
2. symbol_versions.origin_type in (official, local, imported)
3. symbol_connectors.kind in (arrive, leave, tee, spindle)
4. symbol_segments.segment_type in (line, arc, polyline, polygon, ellipse)
5. sync_conflicts.status in (open, resolved)
6. sync_conflicts.resolution in (accept_upstream, keep_local, merged_manual)

### 5.2 Проверки атрибутов

1. orientation in (0, 1, 2, 3)
2. flow_arrow in (0, 1, 2)
3. dimensioned in (0, 1, 2)
4. tracing in (0, 1, 2)
5. insulation in (0, 1, 2)

### 5.3 Целостность текущей версии

1. Для каждого symbols.id только одна запись symbol_versions.is_current=1.
2. Для current-версии обязателен symbol_attributes.

## 6. Индексы (минимум)

1. idx_symbol_versions_symbol_current on symbol_versions(symbol_id, is_current)
2. idx_symbol_segments_symbol_version_seq on symbol_segments(symbol_version_id, seq_no)
3. idx_symbol_connectors_symbol_version_kind on symbol_connectors(symbol_version_id, kind)
4. idx_sync_conflicts_symbol_status on sync_conflicts(symbol_id, status)
5. idx_symbol_change_log_symbol_version on symbol_change_log(symbol_version_id)
6. idx_release_catalogs_source_release on release_catalogs(source_id, release_version)

## 7. Совместимость с текущей v1 БД

Маппинг для перехода:

1. skeys -> symbols + symbol_versions + symbol_attributes
2. geometry -> symbol_segments
3. (Arrive/Leave/Tee/SpindlePoint из geometry.data) -> symbol_connectors
4. transactions -> symbol_change_log
5. catalog_symbols + app_metadata(last_synced_release_version) -> release_catalogs + symbol_versions

## 8. Минимальный план миграции (001)

1. Создать новые таблицы v2 рядом со старыми.
2. Перенести данные пакетно с валидацией payload_hash.
3. Включить read-path через feature-flag.
4. Переключить write-path после прохождения integration тестов.
5. Стабилизировать и затем удалить legacy таблицы в отдельной миграции.

## 9. Definition of Ready для Gaphor-диаграммы

1. На диаграмме присутствуют все таблицы из раздела Сущности v2.
2. Все связи из раздела Связи выставлены с кратностями.
3. Notes содержат enum/check/index ограничения.
4. Диаграмма сохранена как единый лист и пригодна для ревью команды.
