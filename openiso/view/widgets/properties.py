# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import json
import os
import logging

from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QColor, QPixmap, QTextCharFormat, QSyntaxHighlighter
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QRadioButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
)

from openiso.core.i18n import setup_i18n

_t = setup_i18n()
logger = logging.getLogger(__name__)


def _flag_to_check_state(value):
    return {
        0: Qt.CheckState.PartiallyChecked,
        1: Qt.CheckState.Unchecked,
        2: Qt.CheckState.Checked,
    }.get(value, Qt.CheckState.PartiallyChecked)


class JsonSyntaxHighlighter(QSyntaxHighlighter):
    """Simple JSON syntax highlighter for read-only preview blocks."""

    def __init__(self, parent):
        super().__init__(parent)

        key_format = QTextCharFormat()
        key_format.setForeground(QColor("#005cc5"))
        key_format.setFontWeight(700)

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#22863a"))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#b31d28"))

        literal_format = QTextCharFormat()
        literal_format.setForeground(QColor("#6f42c1"))

        punct_format = QTextCharFormat()
        punct_format.setForeground(QColor("#586069"))

        self._rules = [
            (QRegularExpression(r'"([^"\\]|\\.)*"(?=\s*:)'), key_format),
            (QRegularExpression(r'"([^"\\]|\\.)*"'), string_format),
            (QRegularExpression(r'\b-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?\b'), number_format),
            (QRegularExpression(r'\b(true|false|null)\b'), literal_format),
            (QRegularExpression(r'[\{\}\[\]:,]'), punct_format),
        ]

    def highlightBlock(self, text):
        for pattern, text_format in self._rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), text_format)

class PropertiesWidget(QGroupBox):
    """
    Component for displaying and editing Skey properties.
    """

    def __init__(self, title, icons_path, parent=None):
        super().__init__(title, parent)
        self.icons_library_path = icons_path
        self.setMinimumWidth(300)
        self.grid_properties = QGridLayout()
        self.setLayout(self.grid_properties)

        self.setup_ui()

    def setup_ui(self):
        self.lbl_skey_code = QLabel(_t("Code"))
        self.txt_skey = QLineEdit("")
        self.lbl_alias_code = QLabel(_t("Isogen Code"))
        self.txt_alias_code = QLineEdit("")
        self.lbl_skey_group = QLabel(_t("Group"))
        self.cb_skey_group = QComboBox()
        self.cb_skey_group.setDuplicatesEnabled(False)
        self.lbl_skey_subgroup = QLabel(_t("Subgroup"))
        self.cb_skey_subgroup = QComboBox()

        self.lbl_spindle = QLabel(_t("Spindle"))
        self.cb_spindle_skey = QComboBox()
        self.cb_spindle_skey.setEditable(True)
        self.cb_spindle_skey.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.lbl_source_type = QLabel(_t("Source Type"))
        self.cb_source_type = QComboBox()
        self.cb_source_type.addItem(_t("Standard"), "standard")
        self.cb_source_type.addItem(_t("Company"), "company")
        self.cb_source_type.addItem(_t("Project"), "project")

        self.lbl_source_name = QLabel(_t("Source Name"))
        self.txt_source_name = QLineEdit("")

        self.lbl_source_version = QLabel(_t("Source Version"))
        self.txt_source_version = QLineEdit("")

        self.lbl_pcf_identification = QLabel(_t("PCF Identification"))
        self.txt_pcf_identification = QLineEdit("")

        self.lbl_idf_record = QLabel(_t("IDF Record"))
        self.txt_idf_record = QLineEdit("")

        # Description Group
        self.group_description = QGroupBox(_t("Description"))
        self.lyt_description = QVBoxLayout()
        self.group_description.setLayout(self.lyt_description)
        self.txt_skey_desc = QTextEdit("")
        self.txt_skey_desc.setMaximumHeight(80)
        self.lyt_description.addWidget(self.txt_skey_desc)

        # Orientation Group
        self.group_mirror = QGroupBox(_t("Mirror"))
        self.lyt_mirror = QHBoxLayout()
        self.group_mirror.setLayout(self.lyt_mirror)
        self.mirror_button_group = QButtonGroup(self)

        self.radio_mirrors = []
        self.mirror_labels = []
        orientations = [
            ("simmetrical", _t("Use on symmetrical component")),
            ("non_simmetrical", _t("Use on non-symmetrical component")),
            ("reducer", _t("Use on reducers")),
            ("flange", _t("Use on flanges"))
        ]

        for i, (icon_name, text) in enumerate(orientations):
            container = QVBoxLayout()
            container.setSpacing(6)
            container.setContentsMargins(0, 0, 0, 0)

            icon_label = QLabel()
            icon_label.setFixedSize(52, 52)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setToolTip(text)

            # Try to load icon
            icon_path = os.path.join(self.icons_library_path, 'common', f'orientation_{icon_name}.svg')
            if os.path.exists(icon_path):
                icon_label.setPixmap(QPixmap(icon_path).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

            radio = QRadioButton()
            radio.setToolTip(text)

            container.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
            container.addWidget(radio, alignment=Qt.AlignmentFlag.AlignCenter)

            self.lyt_mirror.addLayout(container)
            self.mirror_button_group.addButton(radio, i)
            self.radio_mirrors.append(radio)
            self.mirror_labels.append(icon_label)

        self.radio_mirrors[0].setChecked(True)

        # Draw Orientation Group
        self.group_draw_orientation = QGroupBox(_t("Orientation"))
        self.group_draw_orientation.setToolTip(_t("Controls the direction in which the symbol is drawn.\nApplies only to certain components, such as supports."))
        self.lyt_draw_orientation = QVBoxLayout()
        self.group_draw_orientation.setLayout(self.lyt_draw_orientation)
        self.cb_orientation = QComboBox()
        _draw_orientation_items = [
            (0, _t("None"), _t("Symbol is drawn along the pipe.")),
            (1, _t("Always Vertical"), _t("Symbol is always drawn vertical.")),
            (2, _t("All Primary"), _t("Symbol copied and drawn in each primary direction (U/D, N/S, E/W).")),
            (3, _t("User Defined"), _t("Direction is controlled by an attribute of the component.")),
        ]
        for _val, _label, _tip in _draw_orientation_items:
            self.cb_orientation.addItem(_label, _val)
            self.cb_orientation.setItemData(self.cb_orientation.count() - 1, _tip, Qt.ItemDataRole.ToolTipRole)
        self.lyt_draw_orientation.addWidget(self.cb_orientation)

        self.chk_flow_arrow = QCheckBox(_t("Flow Arrow"))
        self.chk_flow_arrow.setTristate(True)

        self.chk_dimensioned = QCheckBox(_t("Dimensioned"))
        self.chk_dimensioned.setTristate(True)

        self.chk_tracing = QCheckBox(_t("Tracing"))
        self.chk_tracing.setTristate(True)

        self.chk_insulation = QCheckBox(_t("Insulation"))
        self.chk_insulation.setTristate(True)

        self.chk_user_definable = QCheckBox(_t("User Definable"))
        self.chk_user_definable.setChecked(True)

        self.chk_flow_dependency = QCheckBox(_t("Flow Dependency"))

        self.chk_isogen_standard = QCheckBox(_t("ISOGEN Standard"))

        self.lbl_geometry = QLabel(_t("Symbol JSON"))
        self.lst_geometry = QPlainTextEdit()
        self.lst_geometry.setReadOnly(True)
        self.lst_geometry.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.lst_geometry.setMinimumHeight(60)
        self.lst_geometry.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.geometry_highlighter = JsonSyntaxHighlighter(self.lst_geometry.document())

        # Add to grid
        self.grid_properties.addWidget(self.lbl_skey_code, 0, 0)
        self.grid_properties.addWidget(self.txt_skey, 0, 1)
        self.grid_properties.addWidget(self.lbl_alias_code, 1, 0)
        self.grid_properties.addWidget(self.txt_alias_code, 1, 1)
        self.grid_properties.addWidget(self.lbl_skey_group, 2, 0)
        self.grid_properties.addWidget(self.cb_skey_group, 2, 1)
        self.grid_properties.addWidget(self.lbl_skey_subgroup, 3, 0)
        self.grid_properties.addWidget(self.cb_skey_subgroup, 3, 1)
        self.grid_properties.addWidget(self.lbl_spindle, 4, 0)
        self.grid_properties.addWidget(self.cb_spindle_skey, 4, 1)

        self.grid_properties.addWidget(self.lbl_source_type, 5, 0)
        self.grid_properties.addWidget(self.cb_source_type, 5, 1)
        self.grid_properties.addWidget(self.lbl_source_name, 6, 0)
        self.grid_properties.addWidget(self.txt_source_name, 6, 1)
        self.grid_properties.addWidget(self.lbl_source_version, 7, 0)
        self.grid_properties.addWidget(self.txt_source_version, 7, 1)
        self.grid_properties.addWidget(self.lbl_pcf_identification, 8, 0)
        self.grid_properties.addWidget(self.txt_pcf_identification, 8, 1)
        self.grid_properties.addWidget(self.lbl_idf_record, 9, 0)
        self.grid_properties.addWidget(self.txt_idf_record, 9, 1)

        self.grid_properties.addWidget(self.group_description, 10, 0, 1, 2)
        self.grid_properties.addWidget(self.group_mirror, 11, 0, 1, 2)

        self.grid_properties.addWidget(self.group_draw_orientation, 12, 0, 1, 2)
        self.grid_properties.addWidget(self.chk_flow_arrow, 13, 0, 1, 2)
        self.grid_properties.addWidget(self.chk_dimensioned, 14, 0, 1, 2)
        self.grid_properties.addWidget(self.chk_tracing, 15, 0, 1, 2)
        self.grid_properties.addWidget(self.chk_insulation, 16, 0, 1, 2)
        self.grid_properties.addWidget(self.chk_user_definable, 17, 0, 1, 2)
        self.grid_properties.addWidget(self.chk_flow_dependency, 18, 0, 1, 2)
        self.grid_properties.addWidget(self.chk_isogen_standard, 19, 0, 1, 2)
        self.grid_properties.addWidget(self.lbl_geometry, 20, 0)
        self.grid_properties.addWidget(self.lst_geometry, 21, 0, 1, 2)
        self.grid_properties.setRowStretch(21, 1)

        self._apply_hidden_properties_for_v090_todo()

    def _apply_hidden_properties_for_v090_todo(self):
        """Hide deferred fields in Properties panel until v0.9.0 scope is finalized."""
        # TODO(v0.9.0): Re-enable these fields after UX/data-model finalization.
        hidden_widgets = [
            self.lbl_skey_code,
            self.txt_skey,
            self.lbl_source_type,
            self.cb_source_type,
            self.lbl_source_name,
            self.txt_source_name,
            self.lbl_source_version,
            self.txt_source_version,
            self.lbl_pcf_identification,
            self.txt_pcf_identification,
            self.lbl_idf_record,
            self.txt_idf_record,
            self.chk_isogen_standard,
            self.chk_user_definable,
        ]
        for widget in hidden_widgets:
            widget.setVisible(False)

    def clear_fields(self):
        """Clears all input fields in the properties widget."""
        self.txt_skey.clear()
        self.txt_alias_code.clear()
        # Keep current items in group combo but deselect
        self.cb_skey_group.setCurrentIndex(0)
        self.cb_skey_subgroup.clear()
        self.cb_skey_subgroup.addItem("", "")
        self.cb_spindle_skey.setCurrentIndex(0)
        self.cb_source_type.setCurrentIndex(0)
        self.txt_source_name.clear()
        self.txt_source_version.clear()
        self.txt_pcf_identification.clear()
        self.txt_idf_record.clear()
        self.txt_skey_desc.setPlainText("")
        self.radio_mirrors[0].setChecked(True)
        self.cb_orientation.setCurrentIndex(0)
        self.chk_flow_arrow.setCheckState(_flag_to_check_state(0))
        self.chk_dimensioned.setCheckState(_flag_to_check_state(0))
        self.chk_tracing.setCheckState(_flag_to_check_state(0))
        self.chk_insulation.setCheckState(_flag_to_check_state(0))
        self.chk_user_definable.setChecked(True)
        self.chk_flow_dependency.setChecked(False)
        self.chk_isogen_standard.setChecked(False)
        self.lst_geometry.setPlainText("{}")

    def update_translations(self, _t):
        """Redraws and re-translates all static UI elements."""
        self.setTitle("")
        self.lbl_alias_code.setText(_t("Alias Code"))
        self.lbl_skey_group.setText(_t("Group"))
        self.lbl_skey_subgroup.setText(_t("Subgroup"))
        self.lbl_spindle.setText(_t("Spindle"))
        # TODO(v0.9.0): Restore translations for deferred fields when re-enabled.

        self.group_description.setTitle(_t("Description"))
        self.group_mirror.setTitle(_t("Orientation"))
        self.group_draw_orientation.setTitle(_t("Orientation"))
        self.group_draw_orientation.setToolTip(_t("Controls the direction in which the symbol is drawn.\nApplies only to certain components, such as supports."))
        _draw_orientation_items = [
            (0, _t("None"), _t("Symbol is drawn along the pipe.")),
            (1, _t("Always Vertical"), _t("Symbol is always drawn vertical.")),
            (2, _t("All Primary"), _t("Symbol copied and drawn in each primary direction (U/D, N/S, E/W).")),
            (3, _t("User Defined"), _t("Direction is controlled by an attribute of the component.")),
        ]
        for _i, (_val, _label, _tip) in enumerate(_draw_orientation_items):
            self.cb_orientation.setItemText(_i, _label)
            self.cb_orientation.setItemData(_i, _tip, Qt.ItemDataRole.ToolTipRole)
        self.chk_flow_arrow.setText(_t("Flow Arrow"))
        self.chk_dimensioned.setText(_t("Dimensioned"))
        self.chk_tracing.setText(_t("Tracing"))
        self.chk_insulation.setText(_t("Insulation"))
        self.chk_flow_dependency.setText(_t("Flow Dependency"))
        self.lbl_geometry.setText(_t("Symbol JSON"))

        orient_texts = [
            _t("Use on symmetrical component"),
            _t("Use on non-symmetrical component"),
            _t("Use on reducers"),
            _t("Use on flanges")
        ]
        for radio, label, text in zip(self.radio_mirrors, self.mirror_labels, orient_texts):
            radio.setToolTip(text)
            label.setToolTip(text)

    def _parse_geometry_json_items(self, geometry):
        """Convert geometry string items into a compact JSON structure."""
        if not geometry:
            return []

        json_items = []
        for item_str in geometry:
            try:
                if not isinstance(item_str, str):
                    json_items.append(self._json_safe(item_str))
                    continue

                parts = item_str.split(":", 1)
                item_type = parts[0].strip()
                params = {}
                if len(parts) > 1:
                    for token in parts[1].strip().split():
                        if "=" in token:
                            key, value = token.split("=", 1)
                            params[key.strip()] = self._coerce_number(value.strip())

                # Compact tuples in valid JSON form:
                # Point: ["ArrivePoint", [x, y], "BW"]
                # Line:  ["Line", [x1, y1], [x2, y2]]
                if item_type in ("ArrivePoint", "LeavePoint", "TeePoint", "SpindlePoint"):
                    x = params.get("x0")
                    y = params.get("y0")
                    point_type = params.get("type")
                    if x is not None and y is not None:
                        compact_item = [item_type, [x, y]]
                        if point_type not in (None, ""):
                            compact_item.append(point_type)
                        json_items.append(compact_item)
                        continue

                if item_type == "Line":
                    x1 = params.get("x1")
                    y1 = params.get("y1")
                    x2 = params.get("x2")
                    y2 = params.get("y2")
                    if None not in (x1, y1, x2, y2):
                        json_items.append([item_type, [x1, y1], [x2, y2]])
                        continue

                # Fallback for other primitives keeps compact pair [type, params].
                json_items.append([item_type, params])
            except (ValueError, TypeError, AttributeError, IndexError) as err:
                logger.warning("Error displaying geometry item: %s", err)
                json_items.append(str(item_str))

        return json_items

    @staticmethod
    def _coerce_number(value):
        """Convert numeric strings to int/float, keep non-numeric values unchanged."""
        try:
            if any(ch in value for ch in (".", "e", "E")):
                return float(value)
            return int(value)
        except (TypeError, ValueError):
            return value

    @staticmethod
    def _json_safe(value):
        """Return a JSON-serializable representation for arbitrary values."""
        try:
            json.dumps(value)
            return value
        except (TypeError, ValueError):
            return str(value)

    def _build_symbol_json_payload(self, geometry):
        """Build a full symbol snapshot from current form fields and geometry."""
        return {
            "skey_code": self.txt_skey.text().strip(),
            "alias_code": self.txt_alias_code.text().strip(),
            "group_key": self.cb_skey_group.currentData() or self.cb_skey_group.currentText(),
            "subgroup_key": self.cb_skey_subgroup.currentData() or self.cb_skey_subgroup.currentText(),
            "description": self.txt_skey_desc.toPlainText(),
            "spindle_skey": self.cb_spindle_skey.currentText(),
            "orientation": self.mirror_button_group.checkedId(),
            "draw_orientation": self.cb_orientation.currentData(),
            "flow_arrow": self.chk_flow_arrow.isChecked(),
            "dimensioned": self.chk_dimensioned.isChecked(),
            "tracing": self.chk_tracing.isChecked(),
            "insulation": self.chk_insulation.isChecked(),
            "user_definable": self.chk_user_definable.isChecked(),
            "flow_dependency": self.chk_flow_dependency.isChecked(),
            "isogen_standard": self.chk_isogen_standard.isChecked(),
            "source": {
                "type": self.cb_source_type.currentData() or "standard",
                "name": self.txt_source_name.text().strip(),
                "version": self.txt_source_version.text().strip(),
                "pcf_identification": self.txt_pcf_identification.text().strip(),
                "idf_record": self.txt_idf_record.text().strip(),
            },
            "geometry": self._parse_geometry_json_items(geometry),
        }

    def display_geometry(self, geometry):
        """Display a full symbol JSON payload (including geometry)."""
        payload = self._build_symbol_json_payload(geometry)
        self.lst_geometry.setPlainText(self._format_symbol_json_payload(payload))

    def _format_symbol_json_payload(self, payload):
        """Format payload with one geometry entry per line for readability."""
        lines = ["{"]
        keys = list(payload.keys())
        for index, key in enumerate(keys):
            value = payload[key]
            is_last = index == len(keys) - 1
            suffix = "," if not is_last else ""

            if key == "geometry":
                lines.append('  "geometry": [')
                for geom_index, item in enumerate(value):
                    geom_suffix = "," if geom_index < len(value) - 1 else ""
                    lines.append(f"    {json.dumps(item, ensure_ascii=False, default=str)}{geom_suffix}")
                lines.append(f"  ]{suffix}")
                continue

            lines.append(
                f'  {json.dumps(key, ensure_ascii=False)}: '
                f'{json.dumps(value, ensure_ascii=False, default=str)}{suffix}'
            )

        lines.append("}")
        return "\n".join(lines)

    def update_spindles(self, spindles):
        """Updates the list of available spindles in the combobox."""
        self.cb_spindle_skey.clear()
        self.cb_spindle_skey.addItem("", "")
        # spindles can be a list of SkeyData objects, tuples (name, description) or strings
        for item in spindles:
            if hasattr(item, 'name'):
                name = item.name
            elif isinstance(item, (list, tuple)):
                name = item[0]
            else:
                name = str(item)
            self.cb_spindle_skey.addItem(name, name)

        # Sort items in combobox (except the first empty one)
        model = self.cb_spindle_skey.model()
        if model:
            model.sort(0, Qt.SortOrder.AscendingOrder)

    def _extract_connection_types(self, geometry):
        """Extract connection type codes from geometry items."""
        if not geometry:
            return []

        types = []
        seen = set()
        for item_str in geometry:
            if not isinstance(item_str, str):
                continue
            parts = item_str.split(":", 1)
            if len(parts) < 2:
                continue
            item_type = parts[0].strip()
            if item_type not in ("ArrivePoint", "LeavePoint", "TeePoint"):
                continue

            params = parts[1].strip().split()
            for param in params:
                if param.startswith("type="):
                    value = param.split("=", 1)[1].strip()
                    if value and value not in seen:
                        seen.add(value)
                        types.append(value)
                    break

        return types

    def _generate_skey_code(self, skey_data):
        """Builds a skey code from group, subgroup, name, and connection types."""
        group_key = skey_data.group_key or ""
        subgroup_key = skey_data.subgroup_key or ""
        name = skey_data.name or ""

        connection_types = self._extract_connection_types(getattr(skey_data, "geometry", None))
        if connection_types:
            types_part = ",".join(connection_types)
            return f"{group_key}-{subgroup_key}-{name}[{types_part}]"

        return f"{group_key}-{subgroup_key}-{name}"

    def load_skey_data(self, skey_data):
        # Capture spindle_skey BEFORE triggering group/subgroup signals that may overwrite skey_data
        spindle_name = skey_data.spindle_skey or ""

        self.txt_skey.setText(skey_data.name or self._generate_skey_code(skey_data))
        self.txt_alias_code.setText(skey_data.name)
        self.cb_skey_group.setCurrentText(_t(skey_data.group_key))
        subgroup_index = self.cb_skey_subgroup.findData(skey_data.subgroup_key)
        if subgroup_index >= 0:
            self.cb_skey_subgroup.setCurrentIndex(subgroup_index)
        else:
            self.cb_skey_subgroup.setCurrentText(skey_data.subgroup_key or "")
        # Set spindle_skey using pre-captured value (skey_data may have been overwritten by signals above)
        if spindle_name:
            spindle_index = self.cb_spindle_skey.findData(spindle_name)
            if spindle_index >= 0:
                self.cb_spindle_skey.setCurrentIndex(spindle_index)
            else:
                spindle_index = self.cb_spindle_skey.findText(spindle_name)
                if spindle_index >= 0:
                    self.cb_spindle_skey.setCurrentIndex(spindle_index)
        else:
            self.cb_spindle_skey.setCurrentIndex(0)
        source_type = getattr(skey_data, "source_type", "standard") or "standard"
        source_index = self.cb_source_type.findData(source_type)
        self.cb_source_type.setCurrentIndex(source_index if source_index >= 0 else 0)
        self.txt_source_name.setText(getattr(skey_data, "source_name", "") or "")
        self.txt_source_version.setText(getattr(skey_data, "source_version", "") or "")
        self.txt_pcf_identification.setText(getattr(skey_data, "pcf_identification", "") or "")
        self.txt_idf_record.setText(getattr(skey_data, "idf_record", "") or "")
        self.txt_skey_desc.setPlainText(_t(skey_data.description_key) or "")

        if 0 <= skey_data.orientation < len(self.radio_mirrors):
            self.radio_mirrors[skey_data.orientation].setChecked(True)

        draw_orientation = getattr(skey_data, "draw_orientation", 0)
        draw_orientation_index = self.cb_orientation.findData(draw_orientation)
        self.cb_orientation.setCurrentIndex(draw_orientation_index if draw_orientation_index >= 0 else 0)

        # FlowArrow: 0=Default, 1=Off, 2=On -> Checkbox: Checked if On
        self.chk_flow_arrow.setCheckState(_flag_to_check_state(skey_data.flow_arrow))
        self.chk_dimensioned.setCheckState(_flag_to_check_state(skey_data.dimensioned))
        self.chk_tracing.setCheckState(_flag_to_check_state(getattr(skey_data, "tracing", 0)))
        self.chk_insulation.setCheckState(_flag_to_check_state(getattr(skey_data, "insulation", 0)))
        self.chk_user_definable.setChecked(getattr(skey_data, "user_definable", 1) == 1)
        self.chk_flow_dependency.setChecked(getattr(skey_data, "flow_dependency", 0) == 1)
        self.chk_isogen_standard.setChecked(getattr(skey_data, "isogen_standard", 0) == 1)
        self.display_geometry(skey_data.geometry)
