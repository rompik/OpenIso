import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit,
                             QLineEdit, QApplication)
from PyQt6.QtCore import pyqtSignal, Qt

class CommandParser:
    """Расширяемый парсер команд (из предыдущего шага)."""
    def __init__(self, canvas_interface):
        self.canvas = canvas_interface
        self.commands = {}
        self._register_default_commands()

    def _register_default_commands(self):
        self.register_command("BY", self._cmd_move)
        self.register_command("ROTATE", self._cmd_rotate)
        self.register_command("CLR", self._cmd_clear)
        self.register_command("HELP", self._cmd_help)

    def register_command(self, name: str, func):
        self.commands[name.upper()] = func

    def parse(self, text: str):
        parts = text.strip().split()
        if not parts:
            return ""
        cmd_name = parts[0].upper()
        args = parts[1:]

        if cmd_name in self.commands:
            try:
                return self.commands[cmd_name](*args)
            except Exception as e:
                return f"Ошибка: {str(e)}"
        return f"Неизвестная команда: {cmd_name}"

    def _cmd_move(self, *args):
        if not args:
            return "Использование: BY <AXIS> <VALUE> [ <AXIS> <VALUE> ... ]"

        results = []
        it = iter(args)
        try:
            for item in it:
                axis = item.upper()
                # Check if it's a known axis
                if axis not in ("X", "Y"):
                    return f"Ошибка: Неизвестная ось {axis}. Используйте X или Y."

                val_str = next(it)
                val = float(val_str)
                res = self.canvas.move_element(axis, val)
                results.append(res)
        except StopIteration:
            return "Ошибка: Ожидалось значение после оси"
        except ValueError:
            return "Ошибка: Некорректное числовое значение"

        # Return unique status messages
        return "\n".join(list(dict.fromkeys(results)))

    def _cmd_rotate(self, angle="90"):
        return self.canvas.rotate_element(angle)

    def _cmd_clear(self):
        return self.canvas.clear_selection()

    def _cmd_help(self, cmd_name=None):
        help_data = {
            "BY": "BY <AXIS> <VALUE> [ <AXIS> <VALUE> ... ] - Переместить выделенное. Оси: X, Y.",
            "ROTATE": "ROTATE [<ANGLE>] - Повернуть выделенное. Угол по умолчанию: 90.",
            "CLR": "CLR - Снять выделение со всех элементов.",
            "HELP": "HELP [<COMMAND>] - Показать список команд или справку по конкретной команде."
        }

        if cmd_name:
            cmd_name = cmd_name.upper()
            if cmd_name in help_data:
                return help_data[cmd_name]
            return f"Нет справки для команды: {cmd_name}"

        return "Доступные команды: " + ", ".join(help_data.keys()) + "\nВведите HELP <COMMAND> для деталей."



