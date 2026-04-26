# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import html

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from openiso.core.i18n import setup_i18n


class SyncConflictsDialog(QDialog):
    """Displays symbols that require manual review after catalog sync."""

    accept_upstream_requested = pyqtSignal(str)
    keep_local_requested = pyqtSignal(str)

    def __init__(self, conflicts: list[dict], sync_result: dict, details_provider=None, parent=None):
        super().__init__(parent)
        self._t = setup_i18n()
        self.conflicts = conflicts
        self.sync_result = sync_result
        self.details_provider = details_provider
        self.setWindowTitle(self._t("Catalog Sync Review"))
        self.resize(980, 620)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        summary = self._t(
            "Official catalog sync completed. Review symbols marked as conflict or upstream_newer before replacing local data."
        )
        layout.addWidget(QLabel(summary))

        self.stats_label = QLabel(
            self._t(
                "Inserted: {inserted}  Updated: {updated}  Conflicts: {conflict}  User-kept: {skipped_user}"
            ).format(
                inserted=self.sync_result.get("inserted", 0),
                updated=self.sync_result.get("updated", 0),
                conflict=self.sync_result.get("conflict", 0),
                skipped_user=self.sync_result.get("skipped_user", 0),
            )
        )
        layout.addWidget(self.stats_label)

        self.table = QTableWidget(len(self.conflicts), 5, self)
        self.table.setHorizontalHeaderLabels(
            [
                self._t("Symbol"),
                self._t("State"),
                self._t("Origin"),
                self._t("Upstream Code"),
                self._t("Upstream Version"),
            ]
        )
        vertical_header = self.table.verticalHeader()
        if vertical_header is not None:
            vertical_header.setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._update_action_buttons)
        self._populate_table()

        header = self.table.horizontalHeader()
        if header is not None:
            header.setStretchLastSection(True)
            header.setMinimumSectionSize(120)
        layout.addWidget(self.table)

        self.details_summary_label = QLabel(self._t("Select a symbol to compare local and upstream versions."))
        layout.addWidget(self.details_summary_label)

        self.legend_label = QLabel(
            self._t("Highlighted rows show differences between local and upstream versions.")
        )
        layout.addWidget(self.legend_label)

        details_splitter = QSplitter(self)
        self.local_details = self._create_details_panel(self._t("Local Version"))
        self.upstream_details = self._create_details_panel(self._t("Upstream Version"))
        details_splitter.addWidget(self.local_details["container"])
        details_splitter.addWidget(self.upstream_details["container"])
        details_splitter.setSizes([1, 1])
        layout.addWidget(details_splitter, stretch=1)

        actions_layout = QHBoxLayout()
        self.accept_upstream_button = QPushButton(self._t("Accept Upstream"), self)
        self.keep_local_button = QPushButton(self._t("Keep Local"), self)
        self.accept_upstream_button.clicked.connect(self._accept_upstream_selected)
        self.keep_local_button.clicked.connect(self._keep_local_selected)
        actions_layout.addWidget(self.accept_upstream_button)
        actions_layout.addWidget(self.keep_local_button)
        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
        self._update_action_buttons()

    def _populate_table(self) -> None:
        self.table.setRowCount(len(self.conflicts))
        for row_index, conflict in enumerate(self.conflicts):
            self.table.setItem(row_index, 0, QTableWidgetItem(conflict.get("name", "")))
            self.table.setItem(row_index, 1, QTableWidgetItem(conflict.get("sync_state", "")))
            self.table.setItem(row_index, 2, QTableWidgetItem(conflict.get("origin_type", "")))
            self.table.setItem(row_index, 3, QTableWidgetItem(conflict.get("upstream_symbol_code", "")))
            self.table.setItem(
                row_index,
                4,
                QTableWidgetItem(str(conflict.get("upstream_symbol_version", 1))),
            )

    def _selected_skey_name(self) -> str:
        current_row = self.table.currentRow()
        if current_row < 0 or current_row >= len(self.conflicts):
            return ""
        return self.conflicts[current_row].get("name", "")

    def _create_details_panel(self, title: str) -> dict:
        container = QWidget(self)
        layout = QVBoxLayout(container)
        title_label = QLabel(title, container)
        metadata = QTextEdit(container)
        geometry = QTextEdit(container)
        metadata.setReadOnly(True)
        geometry.setReadOnly(True)
        metadata.setAcceptRichText(True)
        geometry.setAcceptRichText(True)
        layout.addWidget(title_label)
        layout.addWidget(metadata)
        layout.addWidget(QLabel(self._t("Geometry"), container))
        layout.addWidget(geometry)
        return {"container": container, "metadata": metadata, "geometry": geometry}

    def _snapshot_metadata_rows(self, snapshot: dict | None) -> list[tuple[str, str]]:
        if not snapshot:
            return [(self._t("Status"), self._t("No upstream data available."))]

        return [
            (self._t("Name"), str(snapshot.get("name", ""))),
            (self._t("Group"), str(snapshot.get("group_key", ""))),
            (self._t("Subgroup"), str(snapshot.get("subgroup_key", ""))),
            (self._t("Description"), str(snapshot.get("description_key", ""))),
            (self._t("Origin"), str(snapshot.get("origin_type", ""))),
            (self._t("Sync State"), str(snapshot.get("sync_state", ""))),
            (self._t("Orientation"), str(snapshot.get("orientation", ""))),
            (self._t("Flow Arrow"), str(snapshot.get("flow_arrow", ""))),
            (self._t("Dimensioned"), str(snapshot.get("dimensioned", ""))),
            (self._t("Tracing"), str(snapshot.get("tracing", ""))),
            (self._t("Insulation"), str(snapshot.get("insulation", ""))),
            (self._t("Local Revision"), str(snapshot.get("local_revision", ""))),
            (self._t("Release"), str(snapshot.get("upstream_release_version", ""))),
            (self._t("Upstream Version"), str(snapshot.get("upstream_symbol_version", ""))),
        ]

    def _render_html_lines(self, lines: list[tuple[str, bool]]) -> str:
        rendered = []
        for line, is_changed in lines:
            style = "background-color: #fff0b3;" if is_changed else ""
            rendered.append(
                f"<div style=\"font-family: monospace; white-space: pre-wrap; {style}\">{html.escape(line)}</div>"
            )
        return "".join(rendered)

    def _format_metadata_html(self, snapshot: dict | None, other_snapshot: dict | None) -> str:
        rows = self._snapshot_metadata_rows(snapshot)
        other_rows = self._snapshot_metadata_rows(other_snapshot)
        other_map = {label: value for label, value in other_rows}
        return self._render_html_lines(
            [
                (f"{label}: {value}", other_map.get(label, "") != value)
                for label, value in rows
            ]
        )

    def _format_geometry_html(self, geometry_lines: list[str], other_geometry_lines: list[str]) -> str:
        if not geometry_lines:
            return self._render_html_lines([(self._t("No geometry"), False)])

        other_set = set(other_geometry_lines)
        return self._render_html_lines(
            [(line, line not in other_set) for line in geometry_lines]
        )

    def _update_details_panel(self) -> None:
        skey_name = self._selected_skey_name()
        if not skey_name or self.details_provider is None:
            self.details_summary_label.setText(
                self._t("Select a symbol to compare local and upstream versions.")
            )
            for panel in (self.local_details, self.upstream_details):
                panel["metadata"].clear()
                panel["geometry"].clear()
            return

        details = self.details_provider(skey_name)
        if not details:
            self.details_summary_label.setText(self._t("Comparison data is unavailable for the selected symbol."))
            return

        summary = details.get("summary", {})
        self.details_summary_label.setText(
            self._t(
                "Geometry: local {local_geometry_count}, upstream {upstream_geometry_count}, shared {shared_geometry_count}"
            ).format(
                local_geometry_count=summary.get("local_geometry_count", 0),
                upstream_geometry_count=summary.get("upstream_geometry_count", 0),
                shared_geometry_count=summary.get("shared_geometry_count", 0),
            )
        )

        local_snapshot = details.get("local")
        upstream_snapshot = details.get("upstream")
        local_geometry = list(local_snapshot.get("geometry", [])) if local_snapshot else []
        upstream_geometry = list(upstream_snapshot.get("geometry", [])) if upstream_snapshot else []

        self.local_details["metadata"].setHtml(
            self._format_metadata_html(local_snapshot, upstream_snapshot)
        )
        self.local_details["geometry"].setHtml(
            self._format_geometry_html(local_geometry, upstream_geometry)
        )
        self.upstream_details["metadata"].setHtml(
            self._format_metadata_html(upstream_snapshot, local_snapshot)
        )
        self.upstream_details["geometry"].setHtml(
            self._format_geometry_html(upstream_geometry, local_geometry)
        )

    def _update_action_buttons(self) -> None:
        has_selection = bool(self._selected_skey_name())
        self.accept_upstream_button.setEnabled(has_selection)
        self.keep_local_button.setEnabled(has_selection)
        self._update_details_panel()

    def mark_conflict_resolved(self, skey_name: str) -> None:
        self.conflicts = [conflict for conflict in self.conflicts if conflict.get("name") != skey_name]
        self._populate_table()
        self._update_action_buttons()

    def _accept_upstream_selected(self) -> None:
        skey_name = self._selected_skey_name()
        if not skey_name:
            return
        self.accept_upstream_requested.emit(skey_name)

    def _keep_local_selected(self) -> None:
        skey_name = self._selected_skey_name()
        if not skey_name:
            return
        self.keep_local_requested.emit(skey_name)