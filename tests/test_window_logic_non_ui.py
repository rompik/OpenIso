# SPDX-License-Identifier: MIT

from PyQt6.QtCore import Qt

from openiso.view.main_window.window_canvas import CanvasMixin
from openiso.view.main_window.window_form_adapter import _checkbox_flag_value


def test_checkbox_flag_values_preserve_default_off_and_on():
    assert _checkbox_flag_value(Qt.CheckState.PartiallyChecked) == 0
    assert _checkbox_flag_value(Qt.CheckState.Unchecked) == 1
    assert _checkbox_flag_value(Qt.CheckState.Checked) == 2


def test_canvas_undo_and_redo_delegate_to_scene():
    class _Scene:
        undo_count = 0
        redo_count = 0

        def undo(self):
            self.undo_count += 1

        def redo(self):
            self.redo_count += 1

    class _Window:
        scene = _Scene()

    window = _Window()
    CanvasMixin.undo_last_action(window)
    CanvasMixin.redo_next_action(window)

    assert window.scene.undo_count == 1
    assert window.scene.redo_count == 1