# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""
Repository for Skey data - handles persistence (JSON files)
"""
import json
import os
from typing import Dict, Optional, Any

from openiso.model.skey import SkeyData, SkeyGroup


class SkeyRepository:
	"""Repository for loading and saving Skey data"""

	def __init__(self, skeys_file_path: Optional[str] = None, descriptions_file_path: Optional[str] = None):
		self._skeys: Dict[str, SkeyData] = {}
		self._descriptions: Dict[str, list] = {}
		self._skeys_file_path = skeys_file_path
		self._descriptions_file_path = descriptions_file_path

	@property
	def skeys(self) -> Dict[str, SkeyData]:
		"""Get all skeys"""
		return self._skeys

	@property
	def skeys_dict(self) -> Dict[str, Any]:
		"""Get skeys as raw dictionary for backward compatibility"""
		return {name: skey.to_dict() for name, skey in self._skeys.items()}

	def set_skeys_file_path(self, path: str):
		"""Set the path to the skeys JSON file"""
		self._skeys_file_path = path

	def set_descriptions_file_path(self, path: str):
		"""Set the path to the descriptions JSON file"""
		self._descriptions_file_path = path

	def load_descriptions(self) -> Dict[str, list]:
		"""Load skey descriptions from JSON file"""
		if self._descriptions_file_path and os.path.isfile(self._descriptions_file_path):
			with open(self._descriptions_file_path, 'r', encoding='utf-8') as json_file:
				self._descriptions = json.load(json_file)
		return self._descriptions

	def get_description_info(self, skey_name: str) -> tuple:
		"""Get group and subgroup from descriptions for a skey"""
		if skey_name in self._descriptions:
			desc = self._descriptions[skey_name]
			if isinstance(desc, list) and len(desc) >= 2:
				return (desc[0], desc[1])
		return ("Unknown", "Unknown")

	def load_from_json(self) -> bool:
		"""Load skeys from JSON file"""
		if not self._skeys_file_path or not os.path.isfile(self._skeys_file_path):
			return False

		with open(self._skeys_file_path, 'r', encoding='utf-8') as json_file:
			raw_data = json.load(json_file)
			for name, data in raw_data.items():
				group_key, subgroup_key = self.get_description_info(name)
				skey_data = SkeyData.from_dict(data)
				skey_data.name = name
				skey_data.group_key = group_key
				skey_data.subgroup_key = subgroup_key
				self._skeys[name] = skey_data
		return True


	def build_groups(self) -> SkeyGroup:
		"""Build SkeyGroup structure from loaded skeys"""
		group_obj = SkeyGroup()
		for skey_name, skey_data in self._skeys.items():
			group_obj.add_skey(skey_data.group_key, skey_data.subgroup_key, skey_name)
		return group_obj
