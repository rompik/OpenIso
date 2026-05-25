# Технический шаблон рефакторинга (Спринт 1)

Статус: к исполнению
Горизонт: 1 спринт (5-7 рабочих дней)
Цель: уменьшить связанность UI и бизнес-логики, не ломая текущий функционал и тесты.

## 1. Цели спринта

- Выделить единый `GeometryCodec` для парсинга/сериализации геометрии.
- Вынести синхронизацию каталога в отдельный `CatalogSyncService`.
- Ввести `MainWindowPresenter` для ключевых сценариев окна без полного переписывания UI.
- Сохранить полную обратную совместимость текущих сценариев и тестов.

## 2. Scope (что делаем / что не делаем)

Делаем:
- Вынесение логики из UI-модулей в сервисы и presenter для сценариев `load/save/sync/import`.
- Добавление unit-тестов на новый слой и smoke-проверка UI через существующие тесты.
- Точечная интеграция без изменения формата данных в БД.

Не делаем:
- Полный редизайн классов `SheetLayout` и всех mixin.
- Полный переход на новую схему БД и миграции (это следующий этап).
- Изменение публичного CLI и packaging.

## 3. Целевая структура после спринта

```text
openiso/
  controller/
    services.py                         # фасад совместимости (минимальная логика)
    catalog_sync_service.py             # новый сервис синхронизации каталога
    geometry_codec.py                   # новый единый codec строковой геометрии
  view/
    main_window/
      main_window_presenter.py          # новый presenter для сценариев окна
      window.py                         # тоньше, делегирует операции presenter
      window_geometry_io.py             # использует GeometryCodec
tests/
  test_geometry_codec_non_ui.py         # новый
  test_catalog_sync_service_non_ui.py   # новый
  test_main_window_presenter_non_ui.py  # новый
```

## 4. Контракты модулей (минимум)

### 4.1 GeometryCodec

Файл: `openiso/controller/geometry_codec.py`

Минимальный API:

```python
class GeometryCodec:
    def parse_item(self, raw: str) -> dict: ...
    def parse_many(self, raw_items: list[str]) -> list[dict]: ...
    def serialize_item(self, item: dict) -> str: ...
    def serialize_many(self, items: list[dict]) -> list[str]: ...
```

Требования:
- Поддержка: `ArrivePoint`, `LeavePoint`, `TeePoint`, `SpindlePoint`, `Line`, `Rectangle`, `Polygon`, `Circle`.
- Невалидные строки не должны падать исключением в UI-потоке: возврат `None`/ошибка через результат.
- Round-trip для поддерживаемых примитивов: `serialize(parse(x)) ~= x`.

### 4.2 CatalogSyncService

Файл: `openiso/controller/catalog_sync_service.py`

Минимальный API:

```python
class CatalogSyncService:
    def sync_official_catalog(self, release_version: str) -> dict: ...
    def get_conflicts(self) -> list[dict]: ...
    def get_conflict_details(self, skey_name: str) -> dict | None: ...
    def resolve_accept_upstream(self, skey_name: str) -> bool: ...
    def resolve_keep_local(self, skey_name: str) -> bool: ...
```

Требования:
- Использует `SkeyDB` и доменные модели, но не зависит от Qt.
- Сохраняет текущий контракт возвращаемой статистики (`inserted/updated/conflict/skipped_user`).

### 4.3 MainWindowPresenter

Файл: `openiso/view/main_window/main_window_presenter.py`

Минимальный API:

```python
class MainWindowPresenter:
    def __init__(self, controller, view): ...
    def load_initial_data(self, release_version: str) -> bool: ...
    def load_skey(self, skey_name: str): ...
    def save_current_skey(self, payload: dict, geometry: list[str]) -> bool: ...
    def import_ascii(self, file_path: str): ...
    def import_idf(self, file_path: str): ...
```

Требования:
- `view` передается как интерфейс (duck typing), без импорта Qt в presenter.
- Все side effects UI (status bar, dialogs) остаются в `window.py`, presenter возвращает данные/статусы.

## 5. Пошаговый план внедрения (день за днем)

### День 1
- Создать `GeometryCodec` с unit-тестами парсинга.
- Подключить codec в `window_geometry_io.py` без удаления старых helper-методов.

### День 2
- Перенести сериализацию geometry в codec.
- Добавить round-trip тесты для 6-8 эталонных примитивов.

### День 3
- Вынести sync-логику в `CatalogSyncService`.
- Оставить в `SkeyService` тонкие прокси-методы для обратной совместимости.

### День 4
- Добавить `MainWindowPresenter` и перевести сценарии: `load_initial_data`, `load_skey`.
- Обновить `window.py` на делегирование presenter для этих сценариев.

### День 5
- Перевести `save/import` сценарии на presenter.
- Прогнать все тесты, исправить регрессии, обновить документацию roadmap.

## 6. Технические правила спринта

- Правило совместимости: старые публичные методы (`SkeyService`, `WindowController`) не удалять в этом спринте.
- Любое новое поведение только через тест.
- Один PR = одна логическая задача (codec, sync-service, presenter).
- Каждый PR должен быть ограничен по размеру: до ~500 строк полезных изменений, кроме тестовых фикстур.

## 7. Definition of Done

- Добавлены новые модули: `geometry_codec.py`, `catalog_sync_service.py`, `main_window_presenter.py`.
- Существующие тесты проходят полностью.
- Добавлены минимум 3 новых non-UI тестовых файла.
- Нет прямой зависимости новых сервисов от PyQt6.
- `window.py` стал тоньше по логике сценариев (делегирование presenter).

## 8. Минимальный тест-пакет

Обязательно:
- `pytest tests/test_geometry_codec_non_ui.py`
- `pytest tests/test_catalog_sync_service_non_ui.py`
- `pytest tests/test_main_window_presenter_non_ui.py`
- `pytest tests/test_bootstrap_non_ui.py`
- `pytest tests/test_service_integration_non_ui.py`

Полный контрольный прогон:
- `QT_QPA_PLATFORM=offscreen PYTEST_QT_API=pyqt6 python -m pytest`

## 9. Риски и fallback

Риск:
- Presenter добавит лишний слой и замедлит внедрение.

Fallback:
- Использовать presenter только для 4 сценариев спринта, остальное оставить в `window.py`.

Риск:
- Разъезд форматов geometry между старым кодом и codec.

Fallback:
- Feature flag в `window_geometry_io.py`: временный переключатель `use_geometry_codec`.

## 10. Шаблон PR для задач спринта

```md
## Что сделано
-

## Почему это нужно
-

## Что изменилось по архитектуре
-

## Совместимость
- [ ] Старые публичные методы сохранены
- [ ] Формат данных не изменен

## Тесты
- [ ] Добавлены/обновлены unit-тесты
- [ ] Локально пройден целевой pytest

## Риски
-
```

## 11. Шаблон задач в backlog

1. `REF-101` Ввести `GeometryCodec` + parser tests.
2. `REF-102` Подключить `GeometryCodec` в `window_geometry_io`.
3. `REF-103` Ввести `CatalogSyncService` и прокси в `SkeyService`.
4. `REF-104` Ввести `MainWindowPresenter` для `load_initial_data/load_skey`.
5. `REF-105` Перевести `save/import` в presenter и стабилизировать тесты.

## 12. Артефакты по завершению спринта

- Короткий ADR (1 страница): какие границы слоев закреплены.
- Сводка метрик до/после: размер `window.py`, число методов в `SkeyService`, количество non-UI тестов.
- Обновленный roadmap с фактическим статусом пунктов.
