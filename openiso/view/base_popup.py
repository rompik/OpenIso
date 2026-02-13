import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QPushButton,
    QLabel, QMenu, QWidgetAction, QFrame, QScrollArea
)
from PyQt6.QtGui import QPixmap, QIcon, QPalette, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPainter

class BasePopupItem(QPushButton):
    """Identical to previous, handles individual icon buttons."""
    item_selected = pyqtSignal(str, str) # Emits (category, item_name)

    def __init__(self, category, name, icon_path, size=40, parent=None):
        super().__init__(parent)
        self.category = category
        self.item_name = name
        self.setFixedSize(size + 10, size + 25)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("class", "BasePopupItem")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        self.icon_label = QLabel()
        self.icon_label.setProperty("class", "BasePopupItemIcon")

        if os.path.exists(icon_path):
            # Handle SVG files with currentColor replacement
            if icon_path.endswith('.svg'):
                try:
                    with open(icon_path, 'r', encoding='utf-8') as f:
                        svg_content = f.read()
                    # Replace currentColor with concrete color
                    svg_content = svg_content.replace('currentColor', '#2e3436')

                    # Render modified SVG
                    renderer = QSvgRenderer(svg_content.encode('utf-8'))
                    pixmap = QPixmap(QSize(size, size))
                    pixmap.fill(Qt.GlobalColor.transparent)
                    painter = QPainter(pixmap)
                    renderer.render(painter)
                    painter.end()
                    self.icon_label.setPixmap(pixmap)
                except Exception as e:
                    print(f"[warning] Failed to load SVG {icon_path}: {e}")
                    self.icon_label.setText("❓")
            else:
                # For non-SVG files use standard loading
                icon = QIcon(icon_path)
                pixmap = icon.pixmap(QSize(size, size))
                self.icon_label.setPixmap(pixmap)
        else:
            self.icon_label.setText("❓")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setProperty("class", "BasePopupItemName")

        layout.addWidget(self.icon_label)
        layout.addWidget(self.name_label)
        self.clicked.connect(lambda: self.item_selected.emit(self.category, self.item_name))

class GroupedPopupMenu(QWidget):
    """Popup containing multiple sections (Arrive, Leave, etc.)"""
    selected = pyqtSignal(str, str) # (category, name)

    def __init__(self, title, groups_dict, icons_path, columns=5, parent=None):
        super().__init__(parent)
        self.setFixedWidth(350)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Main Title
        lbl_main = QLabel(title)
        lbl_main.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        main_layout.addWidget(lbl_main)

        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setMaximumHeight(600)

        container = QWidget()
        self.sections_layout = QVBoxLayout(container)
        self.sections_layout.setSpacing(15)

        # Create sections based on the dictionary
        for group_name, items in groups_dict.items():
            self.sections_layout.addWidget(self._create_section(group_name, items, icons_path, columns))

        self.scroll.setWidget(container)
        main_layout.addWidget(self.scroll)

    def _create_section(self, name, items, icons_path, columns):
        """Creates a gray-background frame for a group of items."""
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: #f8f8f8; border-radius: 5px; }")

        layout = QVBoxLayout(frame)

        # Section Title (e.g., 'Arrive Point')
        title = QLabel(name)
        title.setStyleSheet("font-weight: bold; color: #555; background: transparent; padding-left: 5px;")
        layout.addWidget(title)

        grid_widget = QWidget()
        grid_widget.setStyleSheet("background: transparent;")
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 5, 0, 5)

        for i, (item_name, icon_file) in enumerate(items.items()):
            row, col = divmod(i, columns)
            path = os.path.join(icons_path, icon_file)

            btn = BasePopupItem(name, item_name, path)
            btn.item_selected.connect(self.selected.emit)
            grid.addWidget(btn, row, col)

        layout.addWidget(grid_widget)
        return frame

    @staticmethod
    def create_menu(parent_widget, title, groups_dict, icons_path, callback):
        menu = QMenu(parent_widget)
        popup = GroupedPopupMenu(title, groups_dict, icons_path)

        action = QWidgetAction(menu)
        action.setDefaultWidget(popup)
        menu.addAction(action)

        popup.selected.connect(lambda cat, name: [callback(cat, name), menu.close()])
        return menu
