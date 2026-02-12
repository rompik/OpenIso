# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QWidget,
    QStackedWidget
)
from PyQt6.QtGui import QPixmap, QDesktopServices
from PyQt6.QtCore import Qt, QUrl
from openiso.core.i18n import setup_i18n
from openiso.core.constants import (
    REPO_URL, ISSUES_URL, NEW_ISSUE_URL, README_URL, GPL_LICENSE_URL
)
from openiso import __version__

class AboutDialog(QDialog):
    """
    Custom About dialog for the application.
    Redesigned to follow modern GNOME (Adwaita) About window style.
    """
    def __init__(self, icons_path, parent=None):
        super().__init__(parent)
        self.setObjectName("AboutDialog")
        self._t = setup_i18n()
        self.icons_path = icons_path
        self.setWindowTitle(self._t("About"))
        self.setFixedWidth(400)

        # Main layout with stack
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 10)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        self.setupUi()

    def _create_row(self, text, url=None, target_page=None):
        btn = QPushButton()
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setProperty("class", "ListRow")

        layout = QHBoxLayout(btn)
        layout.setContentsMargins(12, 8, 12, 8)

        label = QLabel(text)
        label.setProperty("class", "AboutRowLabel")
        layout.addWidget(label)

        layout.addStretch()

        icon_label = QLabel("↗" if url else "›")
        icon_label.setProperty("class", "AboutRowIcon")
        layout.addWidget(icon_label)

        if url:
            btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
        elif target_page:
            btn.clicked.connect(lambda: self.stack.setCurrentWidget(target_page))

        return btn

    def _create_subpage(self, title):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 5, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 0, 10, 5)

        back_btn = QPushButton("‹")
        back_btn.setObjectName("BackButton")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.main_page))
        header_layout.addWidget(back_btn)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("HeaderTitle")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_lbl, 1)

        # Spacer for centering
        spacer = QWidget()
        spacer.setFixedWidth(28)
        header_layout.addWidget(spacer)

        layout.addWidget(header)

        content_widget = QWidget()
        content_widget.setProperty("class", "SubPageContent")
        layout.addWidget(content_widget, 1)

        return page, content_widget

    def setupUi(self):
        # 1. Main Page Setup
        self.main_page = QWidget()
        self.stack.addWidget(self.main_page)

        content_layout = QVBoxLayout(self.main_page)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(0)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Content for Main Page
        icon_width = int(self.width() * 0.6)
        self.lbl_icon = QLabel()
        icon_path = os.path.join(self.icons_path, "logo.svg")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            self.lbl_icon.setPixmap(pixmap.scaled( icon_width, icon_width, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.lbl_icon)
        content_layout.addSpacing(10)

        self.lbl_title = QLabel("Iso Symbols Library")
        self.lbl_title.setObjectName("AboutTitle")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.lbl_title)

        self.lbl_author = QLabel("Roman PARYGIN")
        self.lbl_author.setObjectName("AboutAuthor")
        self.lbl_author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.lbl_author)
        content_layout.addSpacing(8)

        badge_container = QHBoxLayout()
        badge_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_version_badge = QLabel(__version__)
        self.lbl_version_badge.setObjectName("VersionBadge")
        badge_container.addWidget(self.lbl_version_badge)
        content_layout.addLayout(badge_container)

        content_layout.addSpacing(10)

        # Sections
        website_group = QFrame()
        website_group.setProperty("class", "ListGroup")
        website_layout = QVBoxLayout(website_group)
        website_layout.setContentsMargins(0, 0, 0, 0)
        website_layout.setSpacing(0)
        website_layout.addWidget(self._create_row(self._t("Website"), url=REPO_URL))
        content_layout.addWidget(website_group)
        content_layout.addSpacing(10)

        support_group = QFrame()
        support_group.setProperty("class", "ListGroup")
        support_layout = QVBoxLayout(support_group)
        support_layout.setContentsMargins(0, 0, 0, 0)
        support_layout.setSpacing(0)
        support_layout.addWidget(self._create_row(self._t("Support Questions"), url=ISSUES_URL))
        s1 = QFrame()
        s1.setProperty("class", "Separator")
        support_layout.addWidget(s1)
        support_layout.addWidget(self._create_row(self._t("Report an Issue"), url=NEW_ISSUE_URL))
        s2 = QFrame()
        s2.setProperty("class", "Separator")
        support_layout.addWidget(s2)
        support_layout.addWidget(self._create_row(self._t("Troubleshooting"), url=README_URL))
        content_layout.addWidget(support_group)
        content_layout.addSpacing(10)

        # 2. Sub-pages Setup
        self.credits_page, self.credits_content = self._create_subpage(self._t("Credits"))
        self.legal_page, self.legal_content = self._create_subpage(self._t("Legal"))
        self.acks_page, self.acks_content = self._create_subpage(self._t("Acknowledgments"))

        self.stack.addWidget(self.credits_page)
        self.stack.addWidget(self.legal_page)
        self.stack.addWidget(self.acks_page)

        legal_group = QFrame()
        legal_group.setProperty("class", "ListGroup")
        legal_layout = QVBoxLayout(legal_group)
        legal_layout.setContentsMargins(0, 0, 0, 0)
        legal_layout.setSpacing(0)
        legal_layout.addWidget(self._create_row(self._t("Credits"), target_page=self.credits_page))
        s3 = QFrame()
        s3.setProperty("class", "Separator")
        legal_layout.addWidget(s3)
        legal_layout.addWidget(self._create_row(self._t("Legal"), target_page=self.legal_page))
        s4 = QFrame()
        s4.setProperty("class", "Separator")
        legal_layout.addWidget(s4)
        legal_layout.addWidget(self._create_row(self._t("Acknowledgments"), target_page=self.acks_page))
        content_layout.addWidget(legal_group)

        # Initialize sub-pages content
        self._setup_subpages_content()

    def _setup_subpages_content(self):
        # Credits
        c_layout = QVBoxLayout(self.credits_content)
        c_layout.setContentsMargins(10, 10, 10, 10)
        lbl = QLabel("Roman PARYGIN")
        lbl.setProperty("class", "AboutCreditsText")
        c_layout.addWidget(lbl)
        c_layout.addStretch()

        # Legal
        l_layout = QVBoxLayout(self.legal_content)
        l_layout.setContentsMargins(15, 15, 15, 15)
        l_layout.setSpacing(10)

        cp = QLabel("© 2024 Roman PARYGIN")
        cp.setProperty("class", "AboutCopyrightBold")
        l_layout.addWidget(cp)

        license_text = self._t("This application is distributed without any warranties. More details in {link}.").format(
            link=f'<a href="{GPL_LICENSE_URL}" style="color: #c01c28;">GNU General Public License, {self._t("version 3 or later")}</a>'
        )
        desc = QLabel(license_text)
        desc.setWordWrap(True)
        desc.setOpenExternalLinks(True)
        desc.setProperty("class", "AboutLegalText")
        l_layout.addWidget(desc)
        l_layout.addStretch()

        # Acknowledgments
        a_layout = QVBoxLayout(self.acks_content)
        a_layout.setContentsMargins(15, 15, 15, 15)
        ack = QLabel(self._t("Special thanks to all contributors and users!"))
        ack.setProperty("class", "AboutAcknowledgment")
        a_layout.addWidget(ack)
        a_layout.addStretch()
