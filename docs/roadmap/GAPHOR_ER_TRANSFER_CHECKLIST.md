# Чеклист переноса ER в Gaphor (20 минут)

Цель: быстро собрать рабочую UML/ER-диаграмму базы OpenIso в Gaphor.

Основа:
- `docs/roadmap/OPENISO_DB_ER_FOR_GAPHOR_UML.md`
- `docs/roadmap/OPENISO_DB_ER_FOR_GAPHOR.md`

## 1. Подготовка диаграммы

1. Откройте Gaphor и создайте новый проект.
2. Добавьте диаграмму типа UML Class Diagram.
3. Сохраните файл проекта (например, `OpenIso_DB_ER.gaphor`).

## 2. Создание классов-таблиц

4. Создайте 11 классов и задайте имена таблиц:
   - `app_metadata`
   - `catalog_symbols`
   - `symbol_sources`
   - `skey_groups`
   - `skey_subgroups`
   - `spindles`
   - `spindle_transactions`
   - `spindle_geometry`
   - `skeys`
   - `transactions`
   - `geometry`
5. Для каждого класса установите стереотип `<<table>>`.

## 3. Добавление атрибутов

6. Для каждого класса перенесите атрибуты из `OPENISO_DB_ER_FOR_GAPHOR_UML.md`.
7. Помечайте ключевые поля прямо в имени атрибута:
   - `{PK}` для первичного ключа
   - `{FK}` для внешнего ключа
   - `{UNIQUE}` для уникального поля
   - `{NOT NULL}` для обязательного поля

## 4. Добавление связей (ассоциаций)

8. Добавьте ассоциации и кратности в этом порядке:
   - `skey_groups 1 -> 0..* skey_subgroups`
   - `skey_groups 1 -> 0..* skeys`
   - `skey_groups 1 -> 0..* spindles`
   - `skey_subgroups 1 -> 0..* skeys`
   - `skey_subgroups 1 -> 0..* spindles`
   - `symbol_sources 1 -> 0..* skeys`
   - `symbol_sources 1 -> 0..* spindles`
   - `spindles 1 -> 0..* spindle_transactions`
   - `spindles 1 -> 0..* spindle_geometry`
   - `spindle_transactions 1 -> 0..* spindle_geometry`
   - `spindles 1 -> 0..* skeys` (по `spindles.name = skeys.spindle_skey`)
   - `skeys 1 -> 0..* transactions`
   - `skeys 1 -> 0..* geometry`
   - `transactions 1 -> 0..* geometry`
9. Подпишите ассоциации именами ролей из UML-файла (опционально, но желательно).

## 5. Раскладка на холсте

10. Разместите справочники слева:
    - `symbol_sources`, `skey_groups`, `skey_subgroups`
11. Разместите основные сущности по центру:
    - `skeys`, `spindles`
12. Разместите историю изменений справа:
    - `transactions`, `geometry`, `spindle_transactions`, `spindle_geometry`
13. Разместите служебные таблицы отдельно снизу:
    - `catalog_symbols`, `app_metadata`

## 6. Notes и ограничения

14. Добавьте Notes на диаграмму:
    - CHECK-ограничения для `skeys` и `spindles`
    - уникальные ограничения `skey_subgroups` и `symbol_sources`
    - индексы:
      - `idx_transactions_skey`
      - `idx_geometry_skey_txn`
      - `idx_spindle_geometry_spindle_txn`

## 7. Финальная проверка

15. Быстрая самопроверка перед сохранением:
    - Все 11 таблиц присутствуют.
    - Все PK/FK отмечены.
    - Все 14 связей проставлены и имеют кратности.
    - Добавлены Notes с ключевыми ограничениями.

Готово: диаграмма пригодна для обсуждения миграции и проектирования версии v2.
