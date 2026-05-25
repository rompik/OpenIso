# Единый JSON-формат данных OpenIso (v1)

Статус: утверждено
Дата: 2026-04-22

## 1. Назначение

Этот формат используется как единый внутренний формат обмена символами:
- импорт из ASCII/IDF в единый вид;
- экспорт из единого вида в ASCII/IDF/JSON;
- синхронизация официального каталога и локальной базы.

## 2. Версионирование

- `schema_version` — версия структуры JSON (меняется при изменении полей/вложенности).
- `format_version` — версия формата для релизной коммуникации.

Правила:
1. Если структура изменилась несовместимо, увеличиваем `schema_version`.
2. Если изменения обратимо-совместимые (новые необязательные поля), увеличиваем `format_version`.
3. Для несовместимых изменений обязателен мигратор `schema_version N -> N+1`.

## 3. Структура верхнего уровня

Обязательные поля:
- `format`: строка, фиксированное значение `OpenIso.Canonical`
- `schema_version`: целое число
- `format_version`: строка (например `1.0.0`)
- `generated_at`: строка ISO-8601
- `source`: объект источника
- `symbols`: массив символов

## 4. Объект source

Поля:
- `type`: `official_catalog` | `local_db` | `import_ascii` | `import_idf`
- `name`: имя источника
- `release_version`: версия релиза (опционально)

## 5. Объект symbol

Обязательные поля:
- `symbol_code`: уникальный код символа
- `group_key`: группа
- `subgroup_key`: подгруппа
- `origin`: источник появления символа
- `iso_behavior`: атрибуты поведения символа на изометричке
- `last_change`: информация о последнем изменении
- `geometry`: объект геометрии

Рекомендуемые поля:
- `name`, `description`, `tags`, `lifecycle`, `source_ref`, `connectors`, `attributes`, `attribute_schema_version`

Системные (машинные) поля, не обязательные для ручного ввода инженером:
- `versioning` (ревизии/хэши/синхронизация)

### 5.1 Блок origin

Обязательные поля:
- `kind`: `standard` | `project`

Рекомендуемые поля:
- `standard_ref`: ссылка на стандарт (например ISO/COMPANY-STD)
- `project_ref`: ссылка на проектный источник
- `note`: произвольное пояснение

### 5.2 Блок iso_behavior

Базовые поля поведения на изометричке:
- `orientation_deg`: угол ориентации
- `show_flow_arrow`: показывать стрелку потока
- `depends_on_flow`: зависит ли отображение от направления потока
- `show_dimensions`: отображать размерные элементы
- `user_can_edit`: можно ли менять в проекте

Правило расширяемости:
1. Новые поведенческие атрибуты добавляются в `iso_behavior` или `attributes`.
2. При добавлении обратимо-совместимых полей увеличивается `format_version`.
3. При несовместимых изменениях структуры увеличивается `schema_version`.
4. Для отдельного жизненного цикла набора атрибутов можно использовать `attribute_schema_version`.

### 5.3 Блок last_change

Обязательные поля:
- `date`: дата изменения (ISO-8601)
- `reason`: причина изменения

Рекомендуемые поля:
- `author`: кто внес изменение

## 6. Блок versioning (системный, автозаполняемый)

Поля:
- `upstream_symbol_version`: целое число
- `payload_hash`: строка, формат `sha256:<hex>`
- `local_revision`
- `last_synced_release_version`
- `sync_state`: `synced` | `conflict` | `upstream_newer` | `deprecated_upstream`
- `change_ticket`: ссылка на задачу/тикет изменения

## 7. Блок connectors

Массив объектов:
- `kind`: `arrive` | `leave` | `tee` | `spindle`
- `x`: число
- `y`: число
- `direction`: строка (опционально)
- `meta`: объект (опционально)

## 8. Блок geometry

Поля:
- `units`: например `mm`
- `segments`: массив сегментов
- `areas`: массив областей (опционально, для заливки/штриховки)

Типы сегментов:
- `line`: `x1`, `y1`, `x2`, `y2`
- `arc`: `cx`, `cy`, `r`, `start_angle`, `end_angle`
- `polyline`: `points` (массив точек)
- `polygon`: `points`, `closed`
- `ellipse`: `cx`, `cy`, `rx`, `ry`, `rotation`

Типы областей `areas`:
- `fill`: замкнутый контур + параметры заливки (`fill`, `fill_opacity`)
- `hatch`: замкнутый контур + параметры штриховки (`pattern`, `spacing`, `angle`)

Формат области:
- `kind`: `fill` | `hatch`
- `boundary`: замкнутый контур (массив точек)

## 9. Минимальный обязательный набор (MVP)

Для безопасного старта обязателен минимум:
- `format`
- `schema_version`
- `symbols[].symbol_code`
- `symbols[].group_key`
- `symbols[].subgroup_key`
- `symbols[].origin.kind`
- `symbols[].iso_behavior`
- `symbols[].last_change.date`
- `symbols[].last_change.reason`
- `symbols[].geometry.segments`

## 10. Пример JSON

Эталонный файл примера:
- `docs/roadmap/canonical-symbols-v1.example.json`

```json
{
  "format": "OpenIso.Canonical",
  "schema_version": 1,
  "format_version": "1.0.0",
  "generated_at": "2026-04-22T12:00:00Z",
  "source": {
    "type": "official_catalog",
    "name": "OpenIso",
    "release_version": "0.8.0"
  },
  "symbols": [
    {
      "symbol_code": "VAVW",
      "name": "Gate Valve",
      "group_key": "valves",
      "subgroup_key": "gate",
      "description": "Gate valve symbol",
      "origin": {
        "kind": "standard",
        "standard_ref": "ISO-14617",
        "note": "Imported from official standard pack"
      },
      "last_change": {
        "date": "2026-05-23T09:30:00Z",
        "reason": "Added hatch area and updated flow behavior",
        "author": "openiso-team"
      },
      "versioning": {
        "upstream_symbol_version": 7,
        "local_revision": 1,
        "payload_hash": "sha256:9f2ca1bcd5",
        "change_ticket": "OPENISO-241",
        "last_synced_release_version": "0.8.0",
        "sync_state": "synced"
      },
      "connectors": [
        {"kind": "arrive", "x": -22.5, "y": 17.625},
        {"kind": "leave", "x": 22.5, "y": 17.625}
      ],
      "geometry": {
        "units": "mm",
        "segments": [
          {"type": "line", "x1": -22.5, "y1": 17.625, "x2": -15.0, "y2": 17.625},
          {"type": "line", "x1": 19.9, "y1": 25.925, "x2": 22.05, "y2": 20.575}
        ],
        "areas": [
          {
            "id": "area_body_fill",
            "kind": "fill",
            "boundary": [[-8.0, -6.0], [8.0, -6.0], [8.0, 6.0], [-8.0, 6.0]],
            "style": {"fill": "#D9D9D9", "fill_opacity": 0.35}
          },
          {
            "id": "area_body_hatch",
            "kind": "hatch",
            "boundary": [[-7.0, -5.0], [7.0, -5.0], [7.0, 5.0], [-7.0, 5.0]],
            "hatch": {"pattern": "diag_45", "spacing": 1.4, "angle": 45.0}
          }
        ]
      },
      "iso_behavior": {
        "orientation_deg": 0,
        "show_flow_arrow": true,
        "depends_on_flow": false,
        "show_dimensions": true,
        "user_can_edit": true
      },
      "attribute_schema_version": 1,
      "attributes": {
        "insulation_required": false,
        "project_rating": "PN16"
      }
    }
  ]
}
```

## 11. JSON Schema (черновик для валидации)

Файл схемы:
- `docs/roadmap/canonical-symbols-v1.schema.json`

Схема и пример автоматически проверяются тестом:
- `tests/test_canonical_schema_non_ui.py`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://openiso.dev/schema/canonical-symbols-v1.json",
  "title": "OpenIso Canonical Symbols v1",
  "type": "object",
  "required": ["format", "schema_version", "format_version", "generated_at", "source", "symbols"],
  "properties": {
    "format": {"type": "string", "const": "OpenIso.Canonical"},
    "schema_version": {"type": "integer", "minimum": 1},
    "format_version": {"type": "string"},
    "generated_at": {"type": "string", "format": "date-time"},
    "source": {
      "type": "object",
      "required": ["type", "name"],
      "properties": {
        "type": {"type": "string"},
        "name": {"type": "string"},
        "release_version": {"type": "string"}
      },
      "additionalProperties": true
    },
    "symbols": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["symbol_code", "group_key", "subgroup_key", "origin", "iso_behavior", "last_change", "geometry"],
        "properties": {
          "symbol_code": {"type": "string", "minLength": 1},
          "name": {"type": "string"},
          "group_key": {"type": "string"},
          "subgroup_key": {"type": "string"},
          "description": {"type": "string"},
          "origin": {
            "type": "object",
            "required": ["kind"],
            "properties": {
              "kind": {"type": "string", "enum": ["standard", "project"]},
              "standard_ref": {"type": "string"},
              "project_ref": {"type": "string"},
              "note": {"type": "string"}
            },
            "additionalProperties": true
          },
          "versioning": {
            "type": "object",
            "properties": {
              "upstream_symbol_version": {"type": "integer", "minimum": 1},
              "local_revision": {"type": "integer", "minimum": 1},
              "payload_hash": {"type": "string", "pattern": "^sha256:[a-fA-F0-9]+$"},
              "change_ticket": {"type": "string"},
              "last_synced_release_version": {"type": "string"},
              "sync_state": {
                "type": "string",
                "enum": ["synced", "conflict", "upstream_newer", "deprecated_upstream"]
              }
            },
            "additionalProperties": true
          },
          "connectors": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["kind", "x", "y"],
              "properties": {
                "kind": {"type": "string", "enum": ["arrive", "leave", "tee", "spindle"]},
                "x": {"type": "number"},
                "y": {"type": "number"}
              },
              "additionalProperties": true
            }
          },
          "geometry": {
            "type": "object",
            "required": ["segments"],
            "properties": {
              "units": {"type": "string"},
              "segments": {
                "type": "array",
                "items": {
                  "type": "object",
                  "required": ["type"],
                  "properties": {
                    "type": {"type": "string", "enum": ["line", "arc", "polyline", "polygon", "ellipse"]}
                  },
                  "additionalProperties": true
                }
              },
              "areas": {
                "type": "array",
                "items": {
                  "type": "object",
                  "required": ["kind", "boundary"],
                  "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "kind": {"type": "string", "enum": ["fill", "hatch"]},
                    "boundary": {
                      "type": "array",
                      "items": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2
                      },
                      "minItems": 3
                    },
                    "style": {"type": "object", "additionalProperties": true},
                    "hatch": {"type": "object", "additionalProperties": true}
                  },
                  "additionalProperties": true
                }
              }
            },
            "additionalProperties": true
          },
          "iso_behavior": {
            "type": "object",
            "properties": {
              "orientation_deg": {"type": "number"},
              "show_flow_arrow": {"type": "boolean"},
              "depends_on_flow": {"type": "boolean"},
              "show_dimensions": {"type": "boolean"},
              "user_can_edit": {"type": "boolean"}
            },
            "additionalProperties": true
          },
          "last_change": {
            "type": "object",
            "required": ["date", "reason"],
            "properties": {
              "date": {"type": "string", "format": "date-time"},
              "reason": {"type": "string", "minLength": 1},
              "author": {"type": "string"}
            },
            "additionalProperties": true
          },
          "attribute_schema_version": {"type": "integer", "minimum": 1},
          "attributes": {"type": "object"}
        },
        "additionalProperties": true
      }
    }
  },
  "additionalProperties": false
}
```

## 12. Нормативные правила преобразования (ASCII/IDF -> Canonical)

Ниже зафиксированы обязательные правила для импортёров. Цель: один и тот же вход должен давать одинаковый Canonical-результат.

### 12.1 Общие правила нормализации

1. Все `group_key` и `subgroup_key` приводятся к `snake_case` в нижнем регистре.
2. Координаты округляются до 3 знаков после запятой.
3. Пустые и невалидные сегменты геометрии отбрасываются с записью предупреждения в лог импорта.
4. Поле `symbols[].symbol_code` обязательно и является ключом идемпотентности для синхронизации.
5. `payload_hash` рассчитывается как `sha256:` + SHA256 от JSON payload с `sort_keys=true`.
6. Если у символа есть `geometry.areas`, контуры и параметры областей включаются в payload перед расчетом `payload_hash`.

### 12.2 Маппинг из ASCII

- Источник:
  - `source.type = import_ascii`
  - `source.name = Intergraph ASCII`
- Заголовок символа:
  - `501.new_skey | 501.base_skey -> symbol_code`
  - `orientation -> iso_behavior.orientation_deg`
  - `flow_arrow -> iso_behavior.show_flow_arrow`
  - `dimensioned -> iso_behavior.show_dimensions`
  - `spindle_skey -> attributes.spindle_skey`
  - source catalog -> `origin.kind = standard`
- Геометрия `502`:
  - pen action `1` -> стартовая точка (`arrive` или `spindle`, по бизнес-правилу)
  - pen action `2` -> `segments[].type=line`
  - pen action `3` -> `connectors[].kind=tee`
  - pen action `6` -> `connectors[].kind=spindle`

### 12.3 Маппинг из IDF

- Источник:
  - `source.type = import_idf`
  - `source.name = AVEVA IDF`
- Поля 501-подобной записи маппятся в те же `symbol_code/iso_behavior/attributes`, что и для ASCII.
- Геометрия преобразуется в `geometry.segments` по тем же правилам, что и ASCII, чтобы исключить расхождение при round-trip.

### 12.4 Canonical -> ASCII/IDF (экспорт)

1. При экспорте в legacy-формат сохраняются только поддерживаемые в целевом формате сегменты.
2. Неподдерживаемые сегменты (`ellipse`, сложные `arc`) должны:
  - либо аппроксимироваться ломаной,
  - либо отклоняться с явной ошибкой экспорта (в зависимости от режима strict/compat).
3. `connectors.kind` маппится в pen action таблицу целевого формата без эвристик на этапе экспорта.

## 13. Политика конфликтов версий (v1)

### 13.1 Термины

- Upstream: официальный каталог релиза.
- Local: локальная БД пользователя.
- Базовые поля сравнения: `upstream_symbol_version`, `payload_hash`, `local_revision`, `sync_state`.

### 13.2 Правила принятия решений

1. Если `local.is_user_modified = 0` и `upstream_symbol_version > last_synced_upstream_version`:
  - автообновление,
  - `sync_state = synced`.
2. Если `local.is_user_modified = 1` и хэш upstream изменился:
  - пометка конфликта,
  - `sync_state = conflict`.
3. Если upstream не изменился, а локальная ревизия выросла:
  - сохраняем локальную версию,
  - `sync_state = synced`.
4. Если символ удален из upstream:
  - локально не удаляем автоматически,
  - `sync_state = deprecated_upstream`.

### 13.3 Разрешение конфликта

Поддерживаются два ручных сценария:

1. Accept upstream:
  - локальная запись заменяется upstream-версией,
  - `local_revision += 1`,
  - `last_synced_upstream_version = upstream_symbol_version`,
  - `sync_state = synced`.
2. Keep local:
  - геометрия и атрибуты остаются локальными,
  - `local_revision += 1`,
  - `last_synced_upstream_version = upstream_symbol_version`,
  - `sync_state = synced`.

### 13.4 Инварианты после sync

После любого sync/resolve должны выполняться:

1. Для каждого символа существует однозначный `symbol_code`.
2. `payload_hash` согласован с фактическим payload.
3. `sync_state` принадлежит перечислению: `synced | conflict | upstream_newer | deprecated_upstream`.
4. Операция синхронизации идемпотентна при повторном запуске на том же `release_version`.

## 14. Артефакты Этапа 0

- Формат данных: [docs/roadmap/CANONICAL_JSON_FORMAT_V1.md](docs/roadmap/CANONICAL_JSON_FORMAT_V1.md)
- Правила преобразования и merge/update: [docs/roadmap/CANONICAL_TRANSFORM_AND_MERGE_RULES_V1.md](docs/roadmap/CANONICAL_TRANSFORM_AND_MERGE_RULES_V1.md)

