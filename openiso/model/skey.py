"""
SkeyData and SkeyGroup models for Skey Library
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any
from .enums import Orientation, FlowArrow, Dimensioned, Tracing, Insulation

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
