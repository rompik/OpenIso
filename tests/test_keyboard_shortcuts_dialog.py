# SPDX-License-Identifier: MIT

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from shortcuts_dialog import ShortcutsDialog


def _application():
    return QApplication.instance() or QApplication([])


def test_shortcut_search_matches_keys_and_restores_selected_section():
    app = _application()
    dialog = ShortcutsDialog(shortcuts_data=[
        {
            "group": "Общие",
            "shortcuts": [
                ("Сохранить", "Записать документ", "Ctrl+S"),
                ("Открыть", "Загрузить документ", "Ctrl+O"),
            ],
        },
        {"group": "Редактирование", "shortcuts": [("Отменить", None, "Ctrl+Z")]},
    ])
    dialog.show()
    app.processEvents()

    assert dialog.section_list.isVisible()
    dialog.section_list.setCurrentRow(1)
    dialog.search_entry.setText("CTRL+z")
    assert dialog.section_list.isHidden()
    assert dialog.content_stack.currentWidget() is dialog.search_page
    assert dialog._search_groups[0].isHidden()
    assert dialog._search_groups[1].isVisible()

    dialog.search_entry.clear()
    assert dialog.section_list.isVisible()
    assert dialog.content_stack.currentWidget() is dialog._section_pages[1]
    dialog.close()


def test_search_matches_descriptions_and_shows_empty_state():
    app = _application()
    dialog = ShortcutsDialog(shortcuts_data=[
        {"group": "Общие", "shortcuts": [("Сохранить", "Записать документ", "Ctrl+S")]},
    ])
    dialog.show()
    app.processEvents()

    dialog.search_entry.setText("ЗАПИСАТЬ")
    assert dialog.search_content.currentWidget() is dialog.search_scroll
    assert dialog._search_groups[0].rows[0].isVisible()

    dialog.search_entry.setText("несуществующая команда")
    assert dialog.search_content.currentWidget() is dialog.empty_state
    dialog.close()


def test_add_section_is_included_in_live_search_index():
    app = _application()
    dialog = ShortcutsDialog(shortcuts_data=[])
    dialog.show()
    app.processEvents()
    dialog.search_entry.setText("alt+k")

    dialog.add_section("Новый раздел", [("Специальное действие", None, "Alt+K")])

    app.processEvents()

    assert len(dialog._search_index) == 1
    assert dialog._search_groups[0].isVisible()
    dialog.close()