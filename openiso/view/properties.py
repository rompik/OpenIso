# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import os
from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QHBoxLayout, QListWidget, QVBoxLayout, QCheckBox,
    QRadioButton, QButtonGroup, QTextEdit
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from openiso.core.i18n import setup_i18n

_t = setup_i18n()

class PropertiesWidget(QGroupBox):
    """
    Component for displaying and editing Skey properties.
    """

    def __init__(self, title, icons_path, parent=None):
        super().__init__(title, parent)
        self.icons_library_path = icons_path
        self.setFixedWidth(340)
        self.grid_properties = QGridLayout()
        self.setLayout(self.grid_properties)

        self.setup_ui()

    def setup_ui(self):
        self.lbl_skey_code = QLabel(_t("Code"))
        self.txt_skey = QLineEdit("")
        self.lbl_skey_group = QLabel(_t("Group"))
        self.cb_skey_group = QComboBox()
        self.cb_skey_group.setDuplicatesEnabled(False)
        self.lbl_skey_subgroup = QLabel(_t("Subgroup"))
        self.cb_skey_subgroup = QComboBox()

        self.lbl_spindle = QLabel(_t("Spindle"))
        self.cb_spindle_skey = QComboBox()
        self.cb_spindle_skey.setEditable(True)
        self.cb_spindle_skey.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        # Description Group
        self.group_description = QGroupBox(_t("Description"))
        self.lyt_description = QVBoxLayout()
        self.group_description.setLayout(self.lyt_description)
        self.txt_skey_desc = QTextEdit("")
        self.txt_skey_desc.setMaximumHeight(80)
        self.lyt_description.addWidget(self.txt_skey_desc)

        # Orientation Group
        self.group_orientation = QGroupBox(_t("Orientation"))
        self.lyt_orientation = QHBoxLayout()
        self.group_orientation.setLayout(self.lyt_orientation)
        self.orientation_button_group = QButtonGroup(self)

        self.radio_orientations = []
        self.orientation_labels = []
        orientations = [
            ("simmetrical", _t("Use on symmetrical component")),
            ("non_simmetrical", _t("Use on non-symmetrical component")),
            ("reducer", _t("Use on reducers")),
            ("flange", _t("Use on flanges"))
        ]

        for i, (icon_name, text) in enumerate(orientations):
            container = QVBoxLayout()
            container.setSpacing(6)
            container.setContentsMargins(0, 5, 0, 5)

            icon_label = QLabel()
            icon_label.setFixedSize(56, 56)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setToolTip(text)

            # Try to load icon
            icon_path = os.path.join(self.icons_library_path, 'common', f'orientation_{icon_name}.svg')
            if os.path.exists(icon_path):
                icon_label.setPixmap(QPixmap(icon_path).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                icon_label.setText("🖼️") # Placeholder

            radio = QRadioButton()
            radio.setToolTip(text)

            container.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
            container.addWidget(radio, alignment=Qt.AlignmentFlag.AlignCenter)

            self.lyt_orientation.addLayout(container)
            self.orientation_button_group.addButton(radio, i)
            self.radio_orientations.append(radio)
            self.orientation_labels.append(icon_label)

        self.radio_orientations[0].setChecked(True)

        self.chk_flow_arrow = QCheckBox(_t("Flow Arrow"))

        self.chk_dimensioned = QCheckBox(_t("Dimensioned"))

        self.chk_tracing = QCheckBox(_t("Tracing"))

        self.chk_insulation = QCheckBox(_t("Insulation"))

        self.lbl_geometry = QLabel(_t("Geometry"))
        self.lst_geometry = QListWidget()
        self.lst_geometry.setMaximumHeight(120)
        self.lst_geometry.setMinimumHeight(60)

        self.btn_save = QPushButton(_t("Save Changes to Skey File"))
        self.btn_save.setToolTip(_t("Save Changes to Skey File"))

        # Add to grid
        self.grid_properties.addWidget(self.lbl_skey_code, 0, 0)
        self.grid_properties.addWidget(self.txt_skey, 0, 1)
        self.grid_properties.addWidget(self.lbl_skey_group, 1, 0)
        self.grid_properties.addWidget(self.cb_skey_group, 1, 1)
        self.grid_properties.addWidget(self.lbl_skey_subgroup, 2, 0)
        self.grid_properties.addWidget(self.cb_skey_subgroup, 2, 1)
        self.grid_properties.addWidget(self.lbl_spindle, 3, 0)
        self.grid_properties.addWidget(self.cb_spindle_skey, 3, 1)

        self.grid_properties.addWidget(self.group_description, 4, 0, 1, 2)
        self.grid_properties.addWidget(self.group_orientation, 5, 0, 1, 2)

        self.grid_properties.addWidget(self.chk_flow_arrow, 6, 0, 1, 2)
        self.grid_properties.addWidget(self.chk_dimensioned, 7, 0, 1, 2)
        self.grid_properties.addWidget(self.chk_tracing, 8, 0, 1, 2)
        self.grid_properties.addWidget(self.chk_insulation, 9, 0, 1, 2)
        #self.grid_properties.addWidget(self.lbl_geometry, 10, 0)
        #self.grid_properties.addWidget(self.lst_geometry, 11, 0, 1, 2)
        #self.grid_properties.setRowStretch(10, 1)
        self.grid_properties.addWidget(self.btn_save, 11, 0, 1, 2)

    def clear_fields(self):
        """Clears all input fields in the properties widget."""
        self.txt_skey.clear()
        # Keep current items in group combo but deselect
        self.cb_skey_group.setCurrentIndex(-1)
        self.cb_skey_subgroup.clear()
        self.cb_spindle_skey.setCurrentIndex(0)
        self.txt_skey_desc.setPlainText("")
        self.radio_orientations[0].setChecked(True)
        self.chk_flow_arrow.setChecked(False)
        self.chk_dimensioned.setChecked(False)
        self.chk_tracing.setChecked(False)
        self.chk_insulation.setChecked(False)
        self.lst_geometry.clear()

    def update_translations(self, _t):
        """Redraws and re-translates all static UI elements."""
        self.setTitle(_t("Properties"))
        self.lbl_skey_code.setText(_t("Code"))
        self.lbl_skey_group.setText(_t("Group"))
        self.lbl_skey_subgroup.setText(_t("Subgroup"))
        self.lbl_spindle.setText(_t("Spindle"))
        self.group_description.setTitle(_t("Description"))
        self.group_orientation.setTitle(_t("Orientation"))
        self.chk_flow_arrow.setText(_t("Flow Arrow"))
        self.chk_dimensioned.setText(_t("Dimensioned"))
        self.chk_tracing.setText(_t("Tracing"))
        self.chk_insulation.setText(_t("Insulation"))
        self.lbl_geometry.setText(_t("Geometry"))
        self.btn_save.setText(_t("Save Changes to Skey File"))
        self.btn_save.setToolTip(_t("Save Changes to Skey File"))

        orient_texts = [
            _t("Use on symmetrical component"),
            _t("Use on non-symmetrical component"),
            _t("Use on reducers"),
            _t("Use on flanges")
        ]
        for radio, label, text in zip(self.radio_orientations, self.orientation_labels, orient_texts):
            radio.setToolTip(text)
            label.setToolTip(text)

    def display_geometry(self, geometry):
        """Display geometry items in the list widget"""
        self.lst_geometry.clear()
        if not geometry:
            return

        for item_str in geometry:
            try:
                # Format: "Type: param1=value1 param2=value2"
                parts = item_str.split(':', 1)
                item_type = parts[0].strip()
                params = parts[1].strip() if len(parts) > 1 else ""
                self.lst_geometry.addItem(f"{item_type}: {params}")
            except Exception as e:
                print(f"Error displaying geometry item: {e}")
                self.lst_geometry.addItem(str(item_str))

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

    def load_skey_data(self, skey_data):
        self.txt_skey.setText(skey_data.name)
        self.cb_skey_group.setCurrentText(_t(skey_data.group_key))
        # Use full path for subgroup translation
        subgroup_path = f"{skey_data.group_key}.{skey_data.subgroup_key}"
        self.cb_skey_subgroup.setCurrentText(_t(subgroup_path))
        self.cb_spindle_skey.setCurrentText(skey_data.spindle_skey or "")
        self.txt_skey_desc.setPlainText(_t(skey_data.description_key) or "")

        # Display geometry in the list
        self.display_geometry(skey_data.geometry)

        if 0 <= skey_data.orientation < len(self.radio_orientations):
            self.radio_orientations[skey_data.orientation].setChecked(True)

        # FlowArrow: 0=Default, 1=Off, 2=On -> Checkbox: Checked if On
        self.chk_flow_arrow.setChecked(skey_data.flow_arrow == 2)
        # Dimensioned: 0=Default, 1=Off, 2=On -> Checkbox: Checked if On
        self.chk_dimensioned.setChecked(skey_data.dimensioned == 2)
        # Tracing: 0=Default, 1=Off, 2=On -> Checkbox: Checked if On
        self.chk_tracing.setChecked(hasattr(skey_data, 'tracing') and skey_data.tracing == 2)
        # Insulation: 0=Default, 1=Off, 2=On -> Checkbox: Checked if On
        self.chk_insulation.setChecked(hasattr(skey_data, 'insulation') and skey_data.insulation == 2)
        self.display_geometry(skey_data.geometry)
