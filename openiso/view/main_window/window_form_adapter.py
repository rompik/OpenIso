# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""Adapter for extracting form data from Skey properties widget."""

from __future__ import annotations


class WindowFormAdapter:
    """Extract normalized primitive values from UI widgets."""

    def __init__(self, properties_widget):
        self._props = properties_widget

    def collect_save_form_data(self) -> dict:
        return {
            "alias_code": self._props.txt_alias_code.text().strip(),
            "skey_name": self._props.txt_skey.text().strip(),
            "group_key": self._props.cb_skey_group.currentData() or self._props.cb_skey_group.currentText(),
            "subgroup_key": self._props.cb_skey_subgroup.currentData() or self._props.cb_skey_subgroup.currentText(),
            "description_text": self._props.txt_skey_desc.toPlainText(),
            "spindle_skey": self._props.cb_spindle_skey.currentText(),
            "orientation": self._props.orientation_button_group.checkedId(),
            "flow_arrow": 2 if self._props.chk_flow_arrow.isChecked() else 1,
            "dimensioned": 2 if self._props.chk_dimensioned.isChecked() else 1,
            "tracing": 2 if self._props.chk_tracing.isChecked() else 1,
            "insulation": 2 if self._props.chk_insulation.isChecked() else 1,
            "user_definable": 1 if self._props.chk_user_definable.isChecked() else 0,
            "flow_dependency": 1 if self._props.chk_flow_dependency.isChecked() else 0,
            "isogen_standard": 1 if self._props.chk_isogen_standard.isChecked() else 0,
            "source_type": self._props.cb_source_type.currentData() or "standard",
            "source_name": self._props.txt_source_name.text().strip(),
            "source_version": self._props.txt_source_version.text().strip(),
            "pcf_identification": self._props.txt_pcf_identification.text().strip(),
            "idf_record": self._props.txt_idf_record.text().strip(),
        }

    def collect_export_form_data(self) -> dict:
        return {
            "skey_name": self._props.txt_skey.text().strip(),
            "group_key": self._props.cb_skey_group.currentData() or self._props.cb_skey_group.currentText(),
            "subgroup_key": self._props.cb_skey_subgroup.currentData() or self._props.cb_skey_subgroup.currentText(),
            "description_text": self._props.txt_skey_desc.toPlainText(),
            "spindle_skey": self._props.cb_spindle_skey.currentText(),
            "orientation": self._props.orientation_button_group.checkedId(),
            "flow_arrow": 2 if self._props.chk_flow_arrow.isChecked() else 1,
            "dimensioned": 2 if self._props.chk_dimensioned.isChecked() else 1,
            "tracing": 2 if self._props.chk_tracing.isChecked() else 1,
            "insulation": 2 if self._props.chk_insulation.isChecked() else 1,
        }
