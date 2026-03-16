# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import os
import markdown
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QTextBrowser, QTreeView, QSplitter
)
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import Qt, QUrl
from openiso.core.constants import PROJECT_ROOT

class HelpWindow(QMainWindow):
    """
    Window for displaying application help in Markdown format.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help - Iso Symbols Library")
        self.resize(1000, 700)

        self.docs_path = os.path.join(PROJECT_ROOT, 'docs')
        if not os.path.exists(self.docs_path):
            os.makedirs(self.docs_path)

        self.setupUi()
        self.load_file("INDEX.MD")

    def setupUi(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Splitter to separate navigation and content
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Navigation Tree
        self.navModel = QFileSystemModel()
        self.navModel.setRootPath(self.docs_path)
        self.navModel.setNameFilters(["*.MD", "*.md"])
        self.navModel.setNameFilterDisables(False)

        self.navTree = QTreeView()
        self.navTree.setModel(self.navModel)
        self.navTree.setRootIndex(self.navModel.index(self.docs_path))

        # Hide columns except Name
        self.navTree.header().hide()
        self.navTree.setIndentation(10)
        self.navTree.setAnimated(True)
        self.navTree.setObjectName("HelpNavTree")
        self.navTree.clicked.connect(self._on_tree_clicked)

        # Content Browser
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setSearchPaths([self.docs_path])
        # Handle internal links
        self.browser.anchorClicked.connect(self._on_anchor_clicked)

        splitter.addWidget(self.navTree)
        splitter.addWidget(self.browser)
        splitter.setSizes([300, 700])

        layout.addWidget(splitter)

    def load_file(self, filename):
        """Loads and renders a markdown file."""
        file_path = os.path.join(self.docs_path, filename)
        if not os.path.exists(file_path):
            # Try lowercase
            file_path = os.path.join(self.docs_path, filename.lower())

        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    html = markdown.markdown(content, extensions=['extra', 'codehilite'])

                    # Load Adwaita-inspired styling from external CSS
                    css_path = os.path.join(PROJECT_ROOT, 'data', 'markdown.css')
                    style_content = ""
                    if os.path.exists(css_path):
                        with open(css_path, 'r', encoding='utf-8') as cf:
                            style_content = cf.read()

                    styled_html = f"""
                    <html>
                    <head>
                    <style>
                        {style_content}
                    </style>
                    </head>
                    <body>
                        <div class="content">
                            {html}
                        </div>
                    </body>
                    </html>
                    """
                    self.browser.setHtml(styled_html)
            except Exception as e:
                self.browser.setHtml(f"<h1>Error</h1><p>Could not load help file: {e}</p>")
        else:
            self.browser.setHtml(f"<h1>Not Found</h1><p>Help file not found: {filename}</p>")

    def _on_tree_clicked(self, index):
        if not self.navModel.isDir(index):
            filename = self.navModel.fileName(index)
            self.load_file(filename)

    def _on_anchor_clicked(self, url):
        """Handles internal markdown links."""
        link = url.toString()
        if link.lower().endswith(".md"):
            self.load_file(link)
        else:
            # External link or non-md file, open in browser if it's external
            if url.scheme() in ["http", "https"]:
                import webbrowser
                webbrowser.open(link)
