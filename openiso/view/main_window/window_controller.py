# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""Controller for coordinating window-level business operations."""

from __future__ import annotations

from openiso.controller.services import SkeyService
from openiso.model.skey import SkeyData


class WindowController:
    """Thin orchestration layer between SkeyEditor UI and SkeyService."""

    def __init__(self, data_path: str, use_db: bool = True):
        self.skey_service = SkeyService(data_path, use_db=use_db)
        self._last_sync_result: dict | None = None

    def load_initial_data(self, release_version: str | None = None) -> bool:
        self.skey_service.load_descriptions()
        if release_version:
            self._last_sync_result = self.skey_service.sync_official_catalog(release_version)
        return self.skey_service.load_skeys()

    def get_last_sync_result(self) -> dict | None:
        return self._last_sync_result

    def get_sync_conflicts(self) -> list[dict]:
        return self.skey_service.get_sync_conflicts()

    def get_sync_conflict_details(self, skey_name: str) -> dict | None:
        return self.skey_service.get_sync_conflict_details(skey_name)

    def resolve_sync_conflict_accept_upstream(self, skey_name: str) -> bool:
        return self.skey_service.resolve_sync_conflict_accept_upstream(skey_name)

    def resolve_sync_conflict_keep_local(self, skey_name: str) -> bool:
        return self.skey_service.resolve_sync_conflict_keep_local(skey_name)

    def load_skeys(self) -> bool:
        return self.skey_service.load_skeys()

    def reload_groups(self) -> None:
        self.skey_service.reload_groups()

    def get_groups(self):
        return self.skey_service.groups

    def get_skey(self, skey_name: str):
        return self.skey_service.get_skey(skey_name)

    def get_subgroup_names(self, group_key: str):
        return self.skey_service.get_subgroup_names(group_key)

    def get_all_spindles(self):
        return self.skey_service.get_all_spindles()

    def delete_skey(self, skey_name: str) -> bool:
        return self.skey_service.delete_skey(skey_name)

    def save_skey(self, **kwargs) -> bool:
        self.skey_service.update_skey(**kwargs)
        return self.skey_service.save_skeys()

    def import_from_ascii(self, file_path: str):
        return self.skey_service.import_from_ascii(file_path)

    def import_from_idf(self, file_path: str):
        return self.skey_service.import_from_idf(file_path)

    def export_skey_to_ascii(self, skey_payload: dict, geometry: list) -> str:
        skey = SkeyData(
            name=skey_payload["name"],
            group_key=skey_payload["group_key"],
            subgroup_key=skey_payload["subgroup_key"],
            description_key=skey_payload["description_key"],
            spindle_skey=skey_payload["spindle_skey"],
            orientation=skey_payload["orientation"],
            flow_arrow=skey_payload["flow_arrow"],
            dimensioned=skey_payload["dimensioned"],
            tracing=skey_payload["tracing"],
            insulation=skey_payload["insulation"],
            geometry=geometry,
        )
        return self.skey_service.export_skey_to_ascii(skey)
