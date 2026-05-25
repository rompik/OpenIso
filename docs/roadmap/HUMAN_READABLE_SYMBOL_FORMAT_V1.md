# Human-Readable формат символов OpenIso (v1)

Статус: draft
Дата: 2026-05-16
Назначение: человеко-читаемое описание символов для проектирования, ревью и импорта в Canonical JSON.

## 1. Почему нужен новый формат

Исторический IDF-формат символов проектировался для очень слабых машин и ограниченных каналов хранения. Это дало компактность, но ухудшило:

- читаемость человеком;
- расширяемость;
- прозрачность ревью и диффов;
- поддержку современных примитивов (кривые, стили, метаданные).

Новый формат нужен как "понятный слой авторинга", который:

1. Удобно читать и редактировать вручную.
2. Однозначно компилируется в Canonical JSON.
3. Сохраняет обратимую связь с legacy IDF там, где это возможно.

## 2. Принципы формата

1. Явность вместо скрытых соглашений.
2. Семантика отдельно от геометрии.
3. Примитивы первого класса (line/arc/polyline/polygon/ellipse).
4. Детализация для человека, нормализация для машины.
5. Предсказуемые ограничения и валидируемые поля.

## 3. Оболочка документа

Минимальная структура символа:

```json
{
  "format": "OpenIso.Symbol.HR",
  "schema_version": 1,
  "symbol": {
    "code": "VAVW",
    "name": "Gate Valve",
    "description": "Gate valve with straight-through bore",
    "group": "valves",
    "subgroup": "gate",
    "units": "mm",
    "origin": { "x": 0.0, "y": 0.0 },
    "classification": {},
    "connectors": [],
    "primitives": [],
    "style": {},
    "meta": {}
  }
}
```

## 4. Координаты и единицы

1. Система координат: декартова 2D.
2. Единицы: `mm` по умолчанию.
3. Начало координат символа: `symbol.origin`.
4. Допускаются отрицательные координаты.
5. Рекомендуемая точность: до 3 знаков после запятой.

## 4.1 Legacy-классификация (SymbolKeys bridge)

Для сохранения данных из таблиц SymbolKeys рекомендуется использовать
явный блок `symbol.classification`, а не только свободный `meta.legacy`.

```json
{
  "pcf_identification": "FLANGE",
  "idf_record": 105,
  "flow_arrow": false,
  "flow_dependency": false,
  "user_definable": true,
  "code_pattern": "FL**",
  "end_condition_tokens": ["BW", "SW", "FL", "SC"],
  "pattern_params": {
    "segments": 3,
    "bend_radius": 2
  }
}
```

Пояснения:

- `pcf_identification` и `idf_record` отражают одноименные колонки SymbolKeys.
- `flow_arrow`, `flow_dependency`, `user_definable` отражают поведенческие флаги из таблиц.
- `code_pattern` позволяет хранить шаблон SKEY (`**`, `@`, `+`).
- `end_condition_tokens` фиксирует допустимые замены для `**`.
- `pattern_params` хранит значения параметров (`@` и `+`) для конкретного символа.

## 5. Коннекторы (семантика потока)

Коннекторы описывают функциональные точки символа, не заменяя графику.

```json
{
  "id": "c_in",
  "kind": "arrive",
  "x": -22.5,
  "y": 0.0,
  "direction": "west",
  "required": true,
  "meta": { "legacy_point_type": "1" }
}
```

Допустимые `kind`:

- `arrive`
- `leave`
- `tee`
- `spindle`
- `aux` (вспомогательная точка)

## 6. Современные примитивы

Каждый примитив имеет поля:

- `id`: уникальный идентификатор в символе.
- `type`: тип примитива.
- `layer`: логический слой (`body`, `axis`, `annotation`, `debug`).
- `style_ref`: ссылка на стиль.
- `data`: геометрические параметры.

### 6.1 line

```json
{
  "id": "p1",
  "type": "line",
  "layer": "body",
  "style_ref": "stroke_main",
  "data": { "x1": -22.5, "y1": 0.0, "x2": -12.0, "y2": 0.0 }
}
```

### 6.2 arc

```json
{
  "id": "p2",
  "type": "arc",
  "layer": "body",
  "style_ref": "stroke_main",
  "data": {
    "cx": 0.0,
    "cy": 0.0,
    "r": 8.0,
    "start_angle": 0.0,
    "end_angle": 180.0,
    "clockwise": false
  }
}
```

### 6.3 polyline

```json
{
  "id": "p3",
  "type": "polyline",
  "layer": "body",
  "style_ref": "stroke_main",
  "data": {
    "points": [[-5.0, -3.0], [0.0, 3.0], [5.0, -3.0]],
    "closed": false
  }
}
```

### 6.4 polygon

```json
{
  "id": "p4",
  "type": "polygon",
  "layer": "body",
  "style_ref": "fill_soft",
  "data": {
    "points": [[-4.0, -4.0], [4.0, -4.0], [4.0, 4.0], [-4.0, 4.0]],
    "closed": true
  }
}
```

### 6.5 ellipse

```json
{
  "id": "p5",
  "type": "ellipse",
  "layer": "body",
  "style_ref": "stroke_main",
  "data": {
    "cx": 0.0,
    "cy": 0.0,
    "rx": 6.0,
    "ry": 4.0,
    "rotation": 0.0
  }
}
```

Формат ограничен простыми графическими примитивами без кривых Безье.

## 7. Стили

Стили вынесены в словарь `symbol.style`:

```json
{
  "stroke_main": {
    "stroke": "#111111",
    "stroke_width": 2.0,
    "line_cap": "round",
    "line_join": "round"
  },
  "fill_soft": {
    "stroke": "#111111",
    "stroke_width": 1.0,
    "fill": "#C8C8C8",
    "fill_opacity": 0.35
  }
}
```

Это делает символ одновременно читаемым и пригодным для визуализации на разных движках.

## 8. Трансформации

Формат поддерживает необязательные трансформации на уровне примитива:

```json
"transform": {
  "translate": [0.0, 0.0],
  "rotate": 0.0,
  "scale": [1.0, 1.0]
}
```

Рекомендация: на этапе хранения в Canonical применять трансформации и сохранять примитивы в нормализованном виде.

## 9. Метаданные для ревью и трассируемости

```json
"meta": {
  "author": "openiso-team",
  "created_at": "2026-05-16T10:00:00Z",
  "updated_at": "2026-05-16T12:30:00Z",
  "source": "import_idf",
  "legacy": {
    "record_501": "...",
    "record_502_count": 12
  },
  "tags": ["valve", "isometric", "gate"]
}
```

## 10. Совместимость с IDF

Ниже минимальный мост между legacy-логикой и новым форматом:

1. pen action `1` -> connector `arrive` или `spindle` по доменному правилу.
2. pen action `2` -> primitive `line`.
3. pen action `3` -> connector `tee`.
4. pen action `6` -> connector `spindle`.

Потери при миграции:

- сложные стили в IDF отсутствуют, поэтому стили в HR-формате задаются дефолтами или шаблонами группы.
- при обратном экспорте в IDF часть `ellipse` может аппроксимироваться.

## 11. Правила валидации

Обязательные проверки:

1. `symbol.code` не пустой и уникален в наборе.
2. `connectors.kind` принадлежит допустимому набору.
3. У каждого примитива уникальный `id`.
4. Числовые поля геометрии конечны (не NaN/Inf).
5. У символа минимум один коннектор `arrive` или `leave`.
6. Для экспортируемых в IDF символов не должно быть unsupported примитивов в strict-режиме.
7. Если задан `classification.pattern_params`, значения `segments` и `bend_radius` должны быть в диапазоне 1..9.

## 12. Пример полного символа

```json
{
  "format": "OpenIso.Symbol.HR",
  "schema_version": 1,
  "symbol": {
    "code": "VAVW",
    "name": "Gate Valve",
    "description": "Gate valve with straight-through bore",
    "group": "valves",
    "subgroup": "gate",
    "units": "mm",
    "origin": { "x": 0.0, "y": 0.0 },
    "classification": {
      "pcf_identification": "VALVE",
      "idf_record": 50,
      "flow_arrow": false,
      "flow_dependency": true,
      "user_definable": true,
      "code_pattern": "VA**",
      "end_condition_tokens": ["BW", "SW", "FL", "SC"],
      "pattern_params": { "segments": 1, "bend_radius": 1 }
    },
    "connectors": [
      { "id": "c_in", "kind": "arrive", "x": -22.5, "y": 0.0, "direction": "west", "required": true },
      { "id": "c_out", "kind": "leave", "x": 22.5, "y": 0.0, "direction": "east", "required": true },
      { "id": "c_sp", "kind": "spindle", "x": 0.0, "y": 12.0, "required": false }
    ],
    "style": {
      "stroke_main": { "stroke": "#111111", "stroke_width": 2.0, "line_cap": "round", "line_join": "round" },
      "fill_soft": { "stroke": "#111111", "stroke_width": 1.0, "fill": "#C8C8C8", "fill_opacity": 0.35 }
    },
    "primitives": [
      {
        "id": "p1",
        "type": "line",
        "layer": "body",
        "style_ref": "stroke_main",
        "data": { "x1": -22.5, "y1": 0.0, "x2": -8.0, "y2": 0.0 }
      },
      {
        "id": "p2",
        "type": "line",
        "layer": "body",
        "style_ref": "stroke_main",
        "data": { "x1": 8.0, "y1": 0.0, "x2": 22.5, "y2": 0.0 }
      },
      {
        "id": "p3",
        "type": "polygon",
        "layer": "body",
        "style_ref": "fill_soft",
        "data": { "points": [[-8.0, -6.0], [8.0, -6.0], [8.0, 6.0], [-8.0, 6.0]], "closed": true }
      },
      {
        "id": "p4",
        "type": "line",
        "layer": "body",
        "style_ref": "stroke_main",
        "data": { "x1": -8.0, "y1": -6.0, "x2": 8.0, "y2": 6.0 }
      },
      {
        "id": "p5",
        "type": "line",
        "layer": "body",
        "style_ref": "stroke_main",
        "data": { "x1": -8.0, "y1": 6.0, "x2": 8.0, "y2": -6.0 }
      }
    ],
    "meta": {
      "source": "import_idf",
      "legacy": { "record_502_count": 11 },
      "tags": ["valve", "gate", "idf-migrated"]
    }
  }
}
```

## 13. Режимы использования в OpenIso

1. Authoring mode (человек): редактирование HR-формата.
2. Compile mode (машина): преобразование в Canonical JSON + вычисление payload_hash.
3. Export mode: преобразование в ASCII/IDF с профилями strict/compat.

## 14. Рекомендуемый следующий шаг

Добавить конвертер:

- `HR Symbol JSON -> Canonical JSON`
- `Canonical JSON -> HR Symbol JSON`

и покрыть round-trip тестами для основных групп символов.

## 15. JSON Schema и эталонный пример

Для автоматической валидации подготовлены:

- Schema: [docs/roadmap/human-readable-symbol-v1.schema.json](docs/roadmap/human-readable-symbol-v1.schema.json)
- Example: [docs/roadmap/human-readable-symbol-v1.example.json](docs/roadmap/human-readable-symbol-v1.example.json)

Рекомендуемая проверка в тестах:

1. Валидировать example-файл по schema.
2. Проверять, что `HR -> Canonical -> HR` сохраняет обязательные семантические поля.
