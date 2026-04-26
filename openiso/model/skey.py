# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""
SkeyData and SkeyGroup models for Skey Library
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .enums import Dimensioned, FlowArrow, Insulation, Orientation, Tracing


@dataclass
class SkeyData:
    name: str
    group_key: str = " "
    subgroup_key: str = " "
    description_key: str = ""
    spindle_skey: str = ""
    orientation: int = Orientation.SYMMETRICAL
    flow_arrow: int = FlowArrow.DEFAULT
    dimensioned: int = Dimensioned.DEFAULT
    tracing: int = Tracing.DEFAULT
    insulation: int = Insulation.DEFAULT
    pcf_identification: str = ""
    idf_record: str = ""
    user_definable: int = 1
    flow_dependency: int = 0
    source_id: int | None = None
    source_name: str = ""
    source_type: str = "standard"
    source_version: str = ""
    isogen_standard: int = 0
    origin_type: str = "user"
    is_official: int = 0
    is_user_modified: int = 0
    upstream_symbol_code: str = ""
    upstream_release_version: str = ""
    upstream_symbol_version: int = 1
    last_synced_upstream_version: int = 1
    upstream_payload_hash: str = ""
    local_revision: int = 1
    sync_state: str = "synced"
    geometry: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "group_key": self.group_key,
            "subgroup_key": self.subgroup_key,
            "description_key": self.description_key,
            "spindle_skey": self.spindle_skey,
            "orientation": self.orientation,
            "flow_arrow": self.flow_arrow,
            "dimensioned": self.dimensioned,
            "tracing": self.tracing,
            "insulation": self.insulation,
            "pcf_identification": self.pcf_identification,
            "idf_record": self.idf_record,
            "user_definable": self.user_definable,
            "flow_dependency": self.flow_dependency,
            "source_id": self.source_id,
            "source_name": self.source_name,
            "source_type": self.source_type,
            "source_version": self.source_version,
            "isogen_standard": self.isogen_standard,
            "origin_type": self.origin_type,
            "is_official": self.is_official,
            "is_user_modified": self.is_user_modified,
            "upstream_symbol_code": self.upstream_symbol_code,
            "upstream_release_version": self.upstream_release_version,
            "upstream_symbol_version": self.upstream_symbol_version,
            "last_synced_upstream_version": self.last_synced_upstream_version,
            "upstream_payload_hash": self.upstream_payload_hash,
            "local_revision": self.local_revision,
            "sync_state": self.sync_state,
            "geometry": self.geometry
        }
    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'SkeyData':
        if isinstance(data, dict):
            return cls(
                name=name,
                group_key=data.get("group_key", data.get("group", " ")),
                subgroup_key=data.get("subgroup_key", data.get("subgroup", " ")),
                description_key=data.get("description_key", data.get("description", "")),
                spindle_skey=data.get("spindle_skey", ""),
                orientation=data.get("orientation", 0),
                flow_arrow=data.get("flow_arrow", 0),
                dimensioned=data.get("dimensioned", 0),
                tracing=data.get("tracing", 0),
                insulation=data.get("insulation", 0),
                pcf_identification=data.get("pcf_identification", ""),
                idf_record=data.get("idf_record", ""),
                user_definable=data.get("user_definable", 1),
                flow_dependency=data.get("flow_dependency", 0),
                source_id=data.get("source_id"),
                source_name=data.get("source_name", ""),
                source_type=data.get("source_type", "standard"),
                source_version=data.get("source_version", ""),
                isogen_standard=data.get("isogen_standard", 0),
                origin_type=data.get("origin_type", "user"),
                is_official=data.get("is_official", 0),
                is_user_modified=data.get("is_user_modified", 0),
                upstream_symbol_code=data.get("upstream_symbol_code", ""),
                upstream_release_version=data.get("upstream_release_version", ""),
                upstream_symbol_version=data.get("upstream_symbol_version", 1),
                last_synced_upstream_version=data.get("last_synced_upstream_version", 1),
                upstream_payload_hash=data.get("upstream_payload_hash", ""),
                local_revision=data.get("local_revision", 1),
                sync_state=data.get("sync_state", "synced"),
                geometry=data.get("geometry", [])
            )
        elif isinstance(data, list) and len(data) >= 2:
            return cls(
                name=name,
                group_key=data[0],
                subgroup_key=data[1] if len(data) > 1 else " "
            )
        else:
            return cls(name=name)

@dataclass
class SkeyGroup:
    groups: Dict[str, Dict[str, List[str]]] = field(default_factory=dict)
    def add_skey(self, group_key: str, subgroup_key: str, skey_name: str):
        if group_key not in self.groups:
            self.groups[group_key] = {}
        if subgroup_key not in self.groups[group_key]:
            self.groups[group_key][subgroup_key] = []
        if skey_name not in self.groups[group_key][subgroup_key]:
            self.groups[group_key][subgroup_key].append(skey_name)
    def get_groups(self) -> List[str]:
        return sorted(self.groups.keys())
    def get_subgroups(self, group_key: str) -> List[str]:
        if group_key in self.groups:
            return sorted(self.groups[group_key].keys())
        return []
    def get_skeys(self, group_key: str, subgroup_key: str) -> List[str]:
        if group_key in self.groups and subgroup_key in self.groups[group_key]:
            return sorted(self.groups[group_key][subgroup_key])
        return []
    def filter(self, search_text: str) -> 'SkeyGroup':
        filtered = SkeyGroup()
        search_upper = search_text.upper()
        for group_key, subgroups in self.groups.items():
            for subgroup_key, skeys in subgroups.items():
                for skey in skeys:
                    if (search_upper in skey.upper() or
                        search_upper in subgroup_key.upper() or
                        search_upper in group_key.upper()):
                        filtered.add_skey(group_key, subgroup_key, skey)
        return filtered
    def clear(self):
        self.groups.clear()
