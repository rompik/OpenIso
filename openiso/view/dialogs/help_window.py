# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import json
import os
from typing import cast

import markdown
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel
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
        self.nav_lang_dir = None

        self.setupUi()
        lang_code, lang_dir = self._get_nav_lang_dir()
        self.nav_lang_dir = lang_dir
        first_item = self._populate_navigation_tree(lang_code, lang_dir)
        if first_item:
            self.load_file(first_item["path"], base_dir=lang_dir)

    def _get_nav_lang_dir(self):
        """Return (lang_code, absolute lang dir) for the best available docs language."""
        lang_code = get_current_language() or "en"
        for code in (lang_code, "en"):
            lang_dir = os.path.join(self.docs_path, code)
            if os.path.exists(os.path.join(lang_dir, "index.json")):
                return code, lang_dir
        try:
            for entry in os.listdir(self.docs_path):
                lang_dir = os.path.join(self.docs_path, entry)
                if os.path.isdir(lang_dir) and os.path.exists(os.path.join(lang_dir, "index.json")):
                    return entry, lang_dir
        except OSError:
            pass
        return "en", os.path.join(self.docs_path, "en")

    def setupUi(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Splitter to separate navigation and content
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Navigation Tree built from the main index markdown file.
        self.navModel = QStandardItemModel(self)
        self.navModel.setHorizontalHeaderLabels(["Contents"])
        self.navTree = QTreeView()
        self.navTree.setModel(self.navModel)

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

    def _populate_navigation_tree(self, _lang_code, lang_dir):
        """Populate navigation tree from docs/{lang}/index.json. Returns first nav item or None."""
        self.navModel.removeRows(0, self.navModel.rowCount())
        root = cast(QStandardItem, self.navModel.invisibleRootItem())

        index_path = os.path.join(lang_dir, "index.json")
        if not os.path.exists(index_path):
            return None

        try:
            with open(index_path, 'r', encoding='utf-8') as handle:
                sections = json.load(handle)
        except (OSError, ValueError):
            return None

        first_item = None
        for section in sections:
            section_node = QStandardItem(section.get("title", ""))
            section_node.setEditable(False)
            section_node.setSelectable(False)
            section_node.setData(None, Qt.ItemDataRole.UserRole)
            root.appendRow(section_node)

            for nav_item in section.get("items", []):
                item = QStandardItem(nav_item["title"])
                item.setEditable(False)
                item.setData(
                    {
                        "path": nav_item["file"],
                        "anchor": nav_item.get("anchor"),
                        "base_dir": lang_dir,
                    },
                    Qt.ItemDataRole.UserRole,
                )
                section_node.appendRow(item)
                if first_item is None:
                    first_item = {"path": nav_item["file"], "base_dir": lang_dir}

        self.navTree.expandAll()
        return first_item

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

    def load_file(self, filename, base_dir=None, anchor=None):
        """Loads and renders a markdown file."""
        file_path = self._resolve_doc_path(filename, base_dir=base_dir)

        if file_path and os.path.exists(file_path):
            try:
                self.current_file_path = file_path
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    html = markdown.markdown(content, extensions=['extra', 'codehilite'])

                    # Load CSS: docs/assets/ first, then fallbacks for installed/source
                    css_path = os.path.join(self.docs_path, 'assets', 'markdown.css')
                    if not os.path.exists(css_path):
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
                        os.path.join(self.docs_path, 'assets'),
                    ])
                    self.browser.setHtml(styled_html)
                    if anchor:
                        self.browser.scrollToAnchor(anchor)
            except (OSError, UnicodeError, ValueError) as e:
                self.browser.setHtml(f"<h1>Error</h1><p>Could not load help file: {e}</p>")
        else:
            self.browser.setHtml(f"<h1>Not Found</h1><p>Help file not found: {filename}</p>")

    def _on_tree_clicked(self, index):
        item = self.navModel.itemFromIndex(index)
        if item is None:
            return

        target = item.data(Qt.ItemDataRole.UserRole)
        if not target:
            self.navTree.setExpanded(index, not self.navTree.isExpanded(index))
            return

        path = target.get("path") or ""
        anchor = target.get("anchor")
        base_dir = target.get("base_dir") or self.nav_lang_dir
        if path:
            self.load_file(path, base_dir=base_dir, anchor=anchor)
        elif anchor:
            self.browser.scrollToAnchor(anchor)

    def _on_anchor_clicked(self, url):
        """Handles internal markdown links."""
        link = url.toString()
        if url.scheme() in ["http", "https"]:
            import webbrowser
            webbrowser.open(link)
            return

        base_dir = os.path.dirname(self.current_file_path) if self.current_file_path else self.docs_path
        path = url.path()
        anchor = url.fragment() or None

        if path.lower().endswith(".md"):
            self.load_file(path, base_dir=base_dir, anchor=anchor)
        elif anchor:
            self.browser.scrollToAnchor(anchor)
