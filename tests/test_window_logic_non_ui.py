# SPDX-License-Identifier: MIT

from types import SimpleNamespace

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QFileDialog

from openiso.view.main_window.window_canvas import CanvasMixin
from openiso.view.main_window.window_form_adapter import _checkbox_flag_value
from openiso.view.main_window import window_skey_ops
from openiso.view.main_window.window_skey_ops import SkeyOpsMixin


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


def test_import_handler_uses_non_native_file_dialog_for_idf(monkeypatch):
    selected_path = r"G:\symbols\sample.idf"

    class _FileDialog:
        FileMode = QFileDialog.FileMode
        Option = QFileDialog.Option
        instance = None

        def __init__(self, parent, title, directory):
            self.parent = parent
            self.title = title
            self.directory = directory
            self.options = []
            _FileDialog.instance = self

        def setFileMode(self, mode):
            self.file_mode = mode

        def setNameFilter(self, name_filter):
            self.name_filter = name_filter

        def setOption(self, option, enabled):
            self.options.append((option, enabled))

        def exec(self):
            return QDialog.DialogCode.Accepted

        def selectedFiles(self):
            return [selected_path]

    class _Controller:
        imported_path = None

        def import_from_idf(self, file_path):
            self.imported_path = file_path
            return SimpleNamespace(success=True, errors=[])

    class _StatusBar:
        def showMessage(self, _message, _timeout):
            pass

    class _Window:
        controller = _Controller()
        status_bar_widget = _StatusBar()
        refreshed = False

        def refresh_skey_tree(self):
            self.refreshed = True

    monkeypatch.setattr(window_skey_ops, "QFileDialog", _FileDialog)
    window = _Window()

    SkeyOpsMixin.import_external_file(window)

    dialog = _FileDialog.instance
    assert dialog.file_mode == QFileDialog.FileMode.ExistingFile
    assert (QFileDialog.Option.DontUseNativeDialog, True) in dialog.options
    assert "*.idf" in dialog.name_filter
    assert window.controller.imported_path == selected_path
    assert window.refreshed is True
