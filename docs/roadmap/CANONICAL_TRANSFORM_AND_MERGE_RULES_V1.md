# Правила преобразования и merge/update для Canonical v1

Статус: утверждено для Этапа 0
Дата: 2026-05-16

## 1. Назначение

Документ фиксирует правила:

1. Преобразования из ASCII и IDF в единый формат OpenIso Canonical.
2. Обратного преобразования из Canonical в legacy-форматы.
3. Разрешения конфликтов между локальной и upstream-версиями символов.

Этот документ является нормативным дополнением к спецификации:
[docs/roadmap/CANONICAL_JSON_FORMAT_V1.md](docs/roadmap/CANONICAL_JSON_FORMAT_V1.md).

## 2. Единицы и координаты

1. Базовая система координат Canonical: декартова, центр листа в (0, 0).
2. `geometry.units` по умолчанию: `mm`.
3. Координаты импортёрами нормализуются и округляются до 3 знаков.
4. Коннекторы всегда хранятся как абсолютные координаты в системе Canonical.

## 3. Маппинг ASCII -> Canonical

## 3.1 Источник

- `source.type = import_ascii`
- `source.name = Intergraph ASCII`

## 3.2 Заголовок символа

- `new_skey | base_skey -> symbol_code`
- `orientation -> attributes.orientation`
- `flow_arrow -> attributes.flow_arrow`
- `dimensioned -> attributes.dimensioned`
- `spindle_skey -> attributes.spindle_skey`

## 3.3 Геометрия

Pen actions:

1. `1` -> точка начала траектории; маппится в `connectors.kind=arrive` (или `spindle` по доменному правилу).
2. `2` -> сегмент `line`.
3. `3` -> `connectors.kind=tee`.
4. `6` -> `connectors.kind=spindle`.

## 3.4 Валидация

1. Некорректная запись строки не валит импорт всего файла.
2. Невалидный символ попадает в список ошибок, остальные продолжают импортироваться.

## 4. Маппинг IDF -> Canonical

## 4.1 Источник

- `source.type = import_idf`
- `source.name = AVEVA IDF`

## 4.2 Поля

1. Поля идентификации и атрибутов маппятся эквивалентно ASCII.
2. Геометрия приводитcя к тем же сегментам Canonical (`line/arc/polyline/polygon/ellipse`).

## 4.3 Равенство результата

При эквивалентном исходном символе из ASCII и IDF Canonical-представление должно совпадать по:

1. `symbol_code`.
2. `geometry.segments` (с допуском округления).
3. `connectors`.

## 5. Экспорт Canonical -> ASCII/IDF

1. Экспортируем только сегменты, поддерживаемые целевым форматом напрямую.
2. Неподдерживаемые сегменты:
   - в режиме `compat`: аппроксимируются;
   - в режиме `strict`: вызывают ошибку экспорта с перечислением проблемных сегментов.
3. Коннекторы экспортируются в pen actions через фиксированную таблицу соответствий.

## 6. Политика merge/update

## 6.1 Входные данные сравнения

Для каждого `symbol_code` сравниваются:

1. `upstream_symbol_version`.
2. `payload_hash`.
3. `is_user_modified`.
4. `local_revision`.
5. `last_synced_upstream_version`.

## 6.2 Автоматические решения

1. Upstream новее, локальных правок нет -> автообновление (`synced`).
2. Upstream равен локально синхронизированной версии -> без изменений (`synced`).
3. Upstream удалил символ -> локально оставить и пометить (`deprecated_upstream`).

## 6.3 Конфликт

Конфликт фиксируется, если одновременно:

1. Upstream payload изменился.
2. Локальный символ отмечен как модифицированный (`is_user_modified = 1`).

В этом случае:

1. `sync_state = conflict`.
2. Автоперезапись запрещена.
3. Требуется ручное решение пользователя.

## 6.4 Ручные стратегии

1. Accept upstream:
   - берем upstream payload;
   - увеличиваем `local_revision`;
   - обновляем `last_synced_upstream_version`;
   - `sync_state = synced`.
2. Keep local:
   - сохраняем локальный payload;
   - увеличиваем `local_revision`;
   - фиксируем `last_synced_upstream_version` как обработанный;
   - `sync_state = synced`.

## 7. Инварианты

После любого merge/update должны выполняться:

1. Уникальность `symbol_code` в рамках набора symbols.
2. `payload_hash` соответствует текущему payload.
3. `sync_state` принадлежит допустимому enum.
4. Повторный sync с тем же `release_version` не меняет данные (идемпотентность).

## 8. Тестовые сценарии (минимум)

1. Round-trip: `ASCII -> Canonical -> ASCII` без потери поддерживаемых сегментов.
2. Round-trip: `IDF -> Canonical -> IDF` без потери поддерживаемых сегментов.
3. Конфликт: локальная правка + новый upstream -> `sync_state=conflict`.
4. Accept upstream и Keep local обновляют ревизии согласно правилам.
