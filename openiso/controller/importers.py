# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""
Importers for Skey files - GUI-independent
"""
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass

from openiso.model.skey import SkeyData, SkeyGroup
from openiso.model.geometry import GeometryConverter

@dataclass
class ImportResult:
    """Result of an import operation"""
    success: bool
    skeys: Dict[str, SkeyData]
    groups: SkeyGroup
    errors: List[str]

class BaseSkeyImporter:
    """Base class for Skey importers"""

    def __init__(self, descriptions: Optional[Dict[str, list]] = None,
                 geometry_converter: Optional[GeometryConverter] = None):
        self.descriptions = descriptions or {}
        self.geometry_converter = geometry_converter or GeometryConverter()
        self._errors: List[str] = []

    def _name_to_key(self, prefix: str, name: str) -> str:
        if not name or name == "Unknown":
            return f"{prefix}.unknown"
        # Clean name: lowercase, replace spaces with underscores, remove special chars
        clean_name = name.lower().replace(" ", "_").replace("-", "_").replace("/", "_").replace("(", "").replace(")", "").replace(",", "")
        import re
        clean_name = re.sub(r'[^a-z0-9_.]', '', clean_name)
        while "__" in clean_name:
            clean_name = clean_name.replace("__", "_")
        return f"{prefix}.{clean_name.strip('_')}"

    def _get_description_info(self, skey_name: str) -> Tuple[str, str]:
        """Get group and subgroup keys from descriptions"""
        if skey_name in self.descriptions:
            desc = self.descriptions[skey_name]
            if isinstance(desc, list) and len(desc) >= 2:
                group_val = desc[0]
                subgroup_val = desc[1]

                group_key = group_val if "." in group_val else self._name_to_key("group", group_val)
                subgroup_key = subgroup_val if "." in subgroup_val else self._name_to_key("subgroup", subgroup_val)

                return (group_key, subgroup_key)
        return ("group.unknown", "subgroup.unknown")

    def _add_to_groups(self, groups: SkeyGroup, group: str, subgroup: str, skey_name: str):
        """Add skey to groups hierarchy"""
        groups.add_skey(group, subgroup, skey_name)

    def import_from_file(self, file_path: str) -> 'ImportResult':
        """Import skeys from file - to be implemented by subclasses"""
        raise NotImplementedError

class ASCIISkeyImporter(BaseSkeyImporter):
    """Importer for ASCII skey files (Intergraph format)"""

    def import_from_file(self, file_path: str) -> ImportResult:
        """Import skeys from ASCII file"""
        skeys: Dict[str, SkeyData] = {}
        groups = SkeyGroup()
        self._errors = []

        try:
            with open(file_path, 'r', encoding='utf-8') as symbol_file:
                contents = symbol_file.readlines()
        except Exception as e:
            self._errors.append(f"Failed to read file: {e}")
            return ImportResult(success=False, skeys={}, groups=SkeyGroup(), errors=self._errors)

        skip_line = False
        new_skey = ""
        base_skey = ""
        geometry: List[Any] = []
        spindle_skey = ""
        orientation = 0
        flow_arrow = 0
        dimensioned = 0

        for line_index, row in enumerate(contents):
            if row[:1] == "!":
                skip_line = True
                continue

            record_type = row[:4].strip()

            if record_type == "501":
                # Save previous skey
                if new_skey or base_skey:
                    target_skey = new_skey if new_skey else base_skey
                    if target_skey in skeys:
                        skeys[target_skey].geometry = self.geometry_converter.convert_graphics(
                            target_skey, geometry
                        )

                geometry = []
                skip_line = False

                # Parse 501 record
                new_skey = row[5:10].strip()
                base_skey = row[11:15].strip()
                spindle_skey = row[16:20].strip()

                try:
                    orientation = int(row[30:37].strip())
                    flow_arrow = int(row[38:45].strip())
                    dimensioned = int(row[46:53].strip())
                except (ValueError, IndexError) as e:
                    self._errors.append(f"Line {line_index + 1}: Failed to parse 501 record: {e}")
                    continue

                # Determine target skey and group info
                target_skey = new_skey if new_skey else base_skey
                if target_skey:
                    skey_group, skey_subgroup = self._get_description_info(target_skey)

                    skeys[target_skey] = SkeyData(
                        name=target_skey,
                        group_key=skey_group,
                        subgroup_key=skey_subgroup,
                        description_key="",
                        spindle_skey=spindle_skey,
                        orientation=orientation,
                        flow_arrow=flow_arrow,
                        dimensioned=dimensioned,
                        geometry=[]
                    )

                    self._add_to_groups(groups, skey_group, skey_subgroup, target_skey)

            elif record_type == "502":
                if skip_line:
                    continue

                try:
                    self._parse_502_record(row, geometry)
                except (ValueError, IndexError) as e:
                    self._errors.append(f"Line {line_index + 1}: Failed to parse 502 record: {e}")
                    continue

                # Check if last line
                if line_index == len(contents) - 1:
                    target_skey = new_skey if new_skey else base_skey
                    if target_skey and target_skey in skeys:
                        skeys[target_skey].geometry = self.geometry_converter.convert_graphics(
                            target_skey, geometry
                        )
                    geometry = []

        return ImportResult(
            success=len(self._errors) == 0,
            skeys=skeys,
            groups=groups,
            errors=self._errors
        )

    def _parse_502_record(self, row: str, geometry: List[Any]):
        """Parse a 502 record and append to geometry"""
        positions = [
            (5, 14, 15, 22, 23, 30),
            (31, 38, 39, 46, 47, 54),
            (55, 63, 64, 70, 71, 78),
            (79, 86, 87, 94, 95, 103)
        ]

        for start_action, end_action, start_x, end_x, start_y, end_y in positions:
            pen_action = row[start_action:end_action].strip()
            pos_x = float(row[start_x:end_x].strip())
            pos_y = float(row[start_y:end_y].strip())

            geometry.append(pen_action)
            geometry.append(pos_x)
            geometry.append(pos_y)


class IDFSkeyImporter(BaseSkeyImporter):
    """Importer for IDF skey files (AVEVA format)"""

    def import_from_file(self, file_path: str) -> ImportResult:
        """Import skeys from IDF file"""
        skeys: Dict[str, SkeyData] = {}
        groups = SkeyGroup()
        self._errors = []

        try:
            with open(file_path, 'r', encoding='utf-8') as symbol_file:
                contents = symbol_file.readlines()
        except Exception as e:
            self._errors.append(f"Failed to read file: {e}")
            return ImportResult(success=False, skeys={}, groups=SkeyGroup(), errors=self._errors)

        skip_line = False
        new_skey = ""
        base_skey = ""
        geometry: List[Any] = []
        spindle_skey = ""
        orientation = 0
        flow_arrow = 0
        dimensioned = 0

        for line_index, row in enumerate(contents):
            if row[:1] == "!":
                skip_line = True
                continue

            record_type = row[:5].strip()

            if record_type == "501":
                # Save previous skey
                if new_skey or base_skey:
                    target_skey = new_skey if new_skey else base_skey
                    if target_skey in skeys:
                        skeys[target_skey].geometry = self.geometry_converter.convert_graphics(
                            target_skey, geometry
                        )

                geometry = []
                skip_line = False

                # Parse 501 record (IDF format uses comma-separated values)
                try:
                    skey_parts = row[5:21].strip().split(",")
                    new_skey = skey_parts[0] if len(skey_parts) > 0 else ""
                    base_skey = skey_parts[1] if len(skey_parts) > 1 else ""
                    spindle_skey = skey_parts[2] if len(skey_parts) > 2 else ""

                    orientation = int(row[30:37].strip())
                    flow_arrow = int(row[38:45].strip())
                    dimensioned = int(row[46:53].strip())
                except (ValueError, IndexError) as e:
                    self._errors.append(f"Line {line_index + 1}: Failed to parse 501 record: {e}")
                    continue

                # Determine target skey and group info
                target_skey = new_skey if new_skey else base_skey
                if target_skey:
                    skey_group, skey_subgroup = self._get_description_info(target_skey)

                    skeys[target_skey] = SkeyData(
                        name=target_skey,
                        group_key=skey_group,
                        subgroup_key=skey_subgroup,
                        description_key="",
                        spindle_skey=spindle_skey,
                        orientation=orientation,
                        flow_arrow=flow_arrow,
                        dimensioned=dimensioned,
                        geometry=[]
                    )

                    self._add_to_groups(groups, skey_group, skey_subgroup, target_skey)

            elif record_type == "502":
                if skip_line:
                    continue

                try:
                    self._parse_502_record(row, geometry)
                except (ValueError, IndexError) as e:
                    self._errors.append(f"Line {line_index + 1}: Failed to parse 502 record: {e}")
                    continue

                # Check if last line
                if line_index == len(contents) - 1:
                    target_skey = new_skey if new_skey else base_skey
                    if target_skey and target_skey in skeys:
                        skeys[target_skey].geometry = self.geometry_converter.convert_graphics(
                            target_skey, geometry
                        )
                    geometry = []

            else:
                # Other record types - finalize current skey
                if new_skey or base_skey:
                    target_skey = new_skey if new_skey else base_skey
                    if target_skey in skeys and skeys[target_skey].geometry == []:
                        skeys[target_skey].geometry = self.geometry_converter.convert_graphics(
                            target_skey, geometry
                        )
                    geometry = []
                    new_skey = ""
                    base_skey = ""

        return ImportResult(
            success=len(self._errors) == 0,
            skeys=skeys,
            groups=groups,
            errors=self._errors
        )

    def _parse_502_record(self, row: str, geometry: List[Any]):
        """Parse a 502 record and append to geometry"""
        positions = [
            (5, 14, 15, 22, 23, 30),
            (31, 38, 39, 46, 47, 54),
            (55, 63, 64, 70, 71, 78),
            (79, 86, 87, 94, 95, 103)
        ]

        for start_action, end_action, start_x, end_x, start_y, end_y in positions:
            pen_action = row[start_action:end_action].strip()
            pos_x = float(row[start_x:end_x].strip())
            pos_y = float(row[start_y:end_y].strip())

            geometry.append(pen_action)
            geometry.append(pos_x)
            geometry.append(pos_y)


class SkeyImporterFactory:
    """Factory for creating appropriate importer based on file extension"""

    @staticmethod
    def create_importer(file_path: str,
                        descriptions: Optional[Dict[str, list]] = None,
                        geometry_converter: Optional[GeometryConverter] = None) -> BaseSkeyImporter:
        """Create appropriate importer based on file extension"""
        if file_path.lower().endswith('.skey'):
            return ASCIISkeyImporter(descriptions, geometry_converter)
        elif file_path.lower().endswith('.idf'):
            return IDFSkeyImporter(descriptions, geometry_converter)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
