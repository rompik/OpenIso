# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import os

import markdown
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QSplitter,
    QTextBrowser,
    QTreeView,
    QWidget,
)

from openiso.core.constants import DATA_ROOT, PROJECT_ROOT
from openiso.core.i18n import get_current_language


class HelpWindow(QMainWindow):
    """
    Window for displaying application help in Markdown format.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help - Iso Symbols Library")
        self.resize(1000, 700)

        source_docs_path = os.path.join(PROJECT_ROOT, 'docs')
        installed_docs_path = os.path.join(DATA_ROOT, 'docs')
        self.docs_path = source_docs_path if os.path.exists(source_docs_path) else installed_docs_path
        if not os.path.exists(self.docs_path):
            os.makedirs(self.docs_path)

        self.current_file_path = None

        self.setupUi()
        self.load_file(self._get_default_index())

    def _get_default_index(self):
        """Return the best default index file using current language fallback to English."""
        lang_code = get_current_language() or "en"
        preferred = os.path.join(lang_code, "INDEX.MD")
        if os.path.exists(os.path.join(self.docs_path, preferred)):
            return preferred

        fallback = os.path.join("en", "INDEX.MD")
        if os.path.exists(os.path.join(self.docs_path, fallback)):
            return fallback

        return "INDEX.MD"

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
        header = self.navTree.header()
        if header is not None:
            header.hide()
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

    def _resolve_doc_path(self, filename, base_dir=None):
        """Resolve markdown path from absolute/relative links and current document context."""
        if os.path.isabs(filename) and os.path.exists(filename):
            return filename

        candidates = []
        if base_dir:
            candidates.append(os.path.join(base_dir, filename))
        if self.current_file_path:
            candidates.append(os.path.join(os.path.dirname(self.current_file_path), filename))
        candidates.append(os.path.join(self.docs_path, filename))

        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate

        lower_candidates = []
        if base_dir:
            lower_candidates.append(os.path.join(base_dir, filename.lower()))
        if self.current_file_path:
            lower_candidates.append(
                os.path.join(os.path.dirname(self.current_file_path), filename.lower())
            )
        lower_candidates.append(os.path.join(self.docs_path, filename.lower()))

        for candidate in lower_candidates:
            if os.path.exists(candidate):
                return candidate

        return None

    def load_file(self, filename, base_dir=None):
        """Loads and renders a markdown file."""
        file_path = self._resolve_doc_path(filename, base_dir=base_dir)

        if file_path and os.path.exists(file_path):
            try:
                self.current_file_path = file_path
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    html = markdown.markdown(content, extensions=['extra', 'codehilite'])

                    # Load Adwaita-inspired styling from external CSS
                    css_path = os.path.join(DATA_ROOT, 'markdown.css')
                    if not os.path.exists(css_path):
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
                    self.browser.setSearchPaths([
                        self.docs_path,
                        os.path.dirname(file_path),
                    ])
                    self.browser.setHtml(styled_html)
            except (OSError, UnicodeError, ValueError) as e:
                self.browser.setHtml(f"<h1>Error</h1><p>Could not load help file: {e}</p>")
        else:
            self.browser.setHtml(f"<h1>Not Found</h1><p>Help file not found: {filename}</p>")

    def _on_tree_clicked(self, index):
        if not self.navModel.isDir(index):
            file_path = self.navModel.filePath(index)
            self.load_file(file_path)

    def _on_anchor_clicked(self, url):
        """Handles internal markdown links."""
        link = url.toString()
        if link.lower().endswith(".md"):
            base_dir = os.path.dirname(self.current_file_path) if self.current_file_path else self.docs_path
            self.load_file(link, base_dir=base_dir)
        else:
            # External link or non-md file, open in browser if it's external
            if url.scheme() in ["http", "https"]:
                import webbrowser
                webbrowser.open(link)
