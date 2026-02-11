# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QLineEdit, QLabel, QApplication)
from PyQt6.QtCore import pyqtSignal, Qt

class CommandLineEdit(QLineEdit):
    """Поле ввода с поддержкой истории (стрелки Вверх/Вниз)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.history = []
        self.history_index = -1
        self.temp_text = ""

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            self._navigate_history(1)
        elif event.key() == Qt.Key.Key_Down:
            self._navigate_history(-1)
        else:
            super().keyPressEvent(event)
            # Сохраняем текущий ввод, если пользователь не в истории
            if self.history_index == -1:
                self.temp_text = self.text()

    def _navigate_history(self, direction):
        if not self.history:
            return

        if self.history_index == -1 and direction == 1:
            self.temp_text = self.text()

        new_index = self.history_index + direction

        if 0 <= new_index < len(self.history):
            self.history_index = new_index
            # history[0] - самая последняя команда
            self.setText(self.history[self.history_index])
        elif new_index == -1:
            self.history_index = -1
            self.setText(self.temp_text)

    def add_to_history(self, text):
        if text and (not self.history or text != self.history[0]):
            self.history.insert(0, text)
        self.history_index = -1


class TerminalWidget(QWidget):
    def __init__(self, parser):
        super().__init__()
        self.parser = parser
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.history_area = QTextEdit()
        self.history_area.setObjectName("TerminalHistory")
        self.history_area.setReadOnly(True)

        self.input_line = CommandLineEdit()
        self.input_line.setObjectName("TerminalInput")
        self.input_line.setPlaceholderText("Введите команду...")

        self.input_label = QLabel(">")
        self.input_label.setObjectName("TerminalPrompt")

        self.input_container = QWidget()
        self.input_container.setObjectName("TerminalInputContainer")
        self.h_input_layout = QHBoxLayout(self.input_container)
        self.h_input_layout.setContentsMargins(0, 0, 0, 0)
        self.h_input_layout.setSpacing(0)
        self.h_input_layout.addWidget(self.input_label)
        self.h_input_layout.addWidget(self.input_line, stretch=1)

        layout.addWidget(self.history_area)
        layout.addWidget(self.input_container)

        self.input_line.returnPressed.connect(self.handle_input)

    def handle_input(self):
        text = self.input_line.text().strip()
        if not text:
            return

        # Добавляем в историю и выводим в консоль
        self.input_line.add_to_history(text)
        self.history_area.append(f"<span style='color: #888;'>&gt; {text}</span>")

        # Парсим
        response = self.parser.parse(text)
        if response:
            self.history_area.append(f"<span style='color: #005f5f;'>{response}</span>")

        self.input_line.clear()
        self.history_area.ensureCursorVisible()