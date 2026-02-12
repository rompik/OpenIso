from typing import Optional
from openiso.model.skey import SkeyGroup, SkeyData
from openiso.controller.repository import SkeyRepository
from openiso.model.geometry import GeometryConverter
from openiso.controller.db import SkeyDB


class GeometryService:
    """
    Service for geometry-related calculations.
    GUI-independent.
    """
    def __init__(self, settings=None):
        self.settings = settings
        self._converter = GeometryConverter(self.settings) if self.settings else GeometryConverter()

    def parse_geometry_item(self, geometry_string: str) -> dict:
        item_type = geometry_string.split(":")[0]
        result = {"type": item_type}
        if item_type in ("ArrivePoint", "LeavePoint", "TeePoint", "SpindlePoint"):
            result["x0"] = str(GeometryConverter.parse_geometry_value(geometry_string, 1))
            result["y0"] = str(GeometryConverter.parse_geometry_value(geometry_string, 2))
        elif item_type == "Line":
            result["x1"] = str(GeometryConverter.parse_geometry_value(geometry_string, 1))
            result["y1"] = str(GeometryConverter.parse_geometry_value(geometry_string, 2))
            result["x2"] = str(GeometryConverter.parse_geometry_value(geometry_string, 3))
            result["y2"] = str(GeometryConverter.parse_geometry_value(geometry_string, 4))
        elif item_type == "Rectangle":
            result["x0"] = str(GeometryConverter.parse_geometry_value(geometry_string, 1))
            result["y0"] = str(GeometryConverter.parse_geometry_value(geometry_string, 2))
            result["width"] = str(GeometryConverter.parse_geometry_value(geometry_string, 3))
            result["height"] = str(GeometryConverter.parse_geometry_value(geometry_string, 4))
        return result


class SkeyService:
    """
    Main service class that coordinates all Skey business logic.
    This class is completely independent of GUI.
    """
    def __init__(self, data_path: Optional[str] = None, use_db: bool = True):
        self._data_path = data_path
        self._repository = SkeyRepository()
        self._geometry_converter = GeometryConverter()
        self._groups = SkeyGroup()
        self._descriptions = {}
        self._use_db = use_db

        # Build database path from data_path
        if data_path:
            import os
            db_path = os.path.join(data_path, 'database', 'openiso.db')
            self._db = SkeyDB(db_path)
        else:
            self._db = SkeyDB()

        if self._use_db:
            self.load_skeys_from_db()
        elif data_path:
            # Optionally implement loading from JSON if needed
            pass

    def reload_groups(self):
        """Reload skeys from DB and rebuild SkeyGroup from current repository data."""
        self.load_skeys_from_db()
        # Пополняем структуру групп из таблиц групп и подгрупп
        db_groups = self._db.get_all_groups()
        for g_key in db_groups:
            if g_key not in self._groups.get_groups():
                self._groups.groups[g_key] = {}

            db_subgroups = self._db.get_subgroups_by_group(g_key)
            for sg_key in db_subgroups:
                if sg_key not in self._groups.groups[g_key]:
                    self._groups.groups[g_key][sg_key] = []

    @property
    def groups(self):
        """Get the current SkeyGroup hierarchy."""
        return self._groups

    def load_descriptions(self) -> bool:
        """Load skey descriptions from the repository."""
        try:
            self._descriptions = self._repository.load_descriptions()
            return True
        except Exception as e:
            print(f"Error loading descriptions: {e}")
            return False

    def load_skeys_from_db(self) -> bool:
        """Load skeys from the database and update groups."""
        try:
            print(f"Loading skeys from database: {self._db.db_path}")
            skeys = self._db.get_all_skeys()
            print(f"Loaded {len(skeys)} skeys from database")
            self._repository.skeys.clear()
            for skey in skeys:
                self._repository.skeys[skey.name] = skey
            self._groups = self._repository.build_groups() if hasattr(self._repository, 'build_groups') else SkeyGroup()
            print(f"Built groups with {len(self._groups.get_groups())} top-level groups")
            return True
        except Exception as e:
            print(f"Error loading skeys from DB: {e}")
            import traceback
            traceback.print_exc()
            return False

    def load_skeys(self) -> bool:
        """Alias for load_skeys_from_db to match expected interface."""
        return self.load_skeys_from_db()

    def delete_skey(self, skey_name: str) -> bool:
        """Delete a skey from the database and refresh the groups."""
        try:
            self._db.delete_skey(skey_name)
            self.reload_groups()
            return True
        except Exception as e:
            print(f"Error deleting skey: {e}")
            return False

    def get_spindle_geometry(self, spindle_name: str) -> list:
        """Fetch geometry for a given spindle name."""
        return self._db.get_spindle_geometry(spindle_name)

    def get_all_spindles(self) -> list:
        """Fetch all spindles from the database."""
        return self._db.get_all_spindles()

    def filter_groups(self, search_text: str):
        """Filter SkeyGroup by search text."""
        return self._groups.filter(search_text)

    def get_subgroup_names(self, group: str):
        """Get subgroup names for a group from database."""
        db_subgroups = self._db.get_subgroups_by_group(group)
        if db_subgroups:
            return db_subgroups

        return self._groups.get_subgroups(group)

    def get_skey(self, name: str):
        """Get a SkeyData by name."""
        return self._repository.skeys.get(name)

    def update_skey(self, name: str, group_key: str, subgroup_key: str, description_key: str,
                   spindle_skey: str, orientation: int,
                   flow_arrow: int, dimensioned: int, tracing: int, insulation: int, geometry: list, lang_code: Optional[str] = None):
        """Update or create a Skey in the database using hierarchical keys."""
        from openiso.core.i18n import save_json_translation


        def clean_key(val):
            if not val: return "unknown"
            for prefix in ["group.", "subgroup.", "description."]:
                if val.startswith(prefix):
                    clean_val = val[len(prefix):]
                    # Если после префикса идет путь (например description.group.subgroup.name), берем последний кусок?
                    # Нет, лучше просто убрать префикс и оставить путь.
                    return clean_val
            return val

        # Нормализуем идентификаторы групп/подгрупп
        g_id = clean_key(group_key).lower().replace(' ', '_').replace('-', '_')
        sg_id = clean_key(subgroup_key).lower().replace(' ', '_').replace('-', '_')

        # Если нам передали не ключ, а текст названия группы/подгруппы, сохраним его перевод
        if "." not in group_key:
            save_json_translation(f"{g_id}._name", group_key, lang_code)
        if "." not in subgroup_key:
            save_json_translation(f"{g_id}.{sg_id}._name", subgroup_key, lang_code)

        # Формируем иерархические ключи для Skey
        name_i18n_key = f"{g_id}.{sg_id}.{name.lower()}"
        desc_i18n_key = f"{name_i18n_key}.description"

        # Сохраняем перевод имени Skey
        save_json_translation(name_i18n_key, name, lang_code)

        if description_key and "." not in description_key and not description_key.startswith("description."):
            save_json_translation(desc_i18n_key, description_key, lang_code)

        skey = SkeyData(
            name=name,
            group_key=g_id,
            subgroup_key=sg_id,
            description_key=desc_i18n_key,
            spindle_skey=spindle_skey,
            orientation=orientation,
            flow_arrow=flow_arrow,
            dimensioned=dimensioned,
            tracing=tracing,
            insulation=insulation,
            geometry=geometry
        )

        # Гарантируем наличие группы и подгруппы в БД
        self._db.ensure_subgroup_exists(g_id, sg_id)

        # Update in database
        self._db.update_skey(skey)

        # Update in repository
        self._repository.skeys[name] = skey

        # Rebuild groups
        self._groups = self._repository.build_groups()

        print(f"Skey '{name}' updated successfully with hierarchy: {g_id} -> {sg_id}")
        return True
    def save_skeys(self):
        """Save all skeys (called after updates)."""
        # Data is already saved in database by update_skey
        # This method is for compatibility
        print("Skeys saved to database")
        return True

    def import_from_ascii(self, file_path: str):
        """Import skeys from ASCII file."""
        from openiso.controller.importers import SkeyImporterFactory
        importer = SkeyImporterFactory.create_importer(file_path, self._descriptions, self._geometry_converter)
        result = importer.import_from_file(file_path)
        if result.success:
            for name, skey in result.skeys.items():
                self._db.update_skey(skey)
                self._repository.skeys[name] = skey
            self._groups = self._repository.build_groups()
        return result

    def import_from_idf(self, file_path: str):
        """Import skeys from IDF file."""
        return self.import_from_ascii(file_path)

    def export_skey_to_ascii(self, skey: SkeyData) -> str:
        """
        Convert a SkeyData object to Intergraph ASCII format (lines of 501 and 502 records).
        """
        # 1. Header 501
        # Format: 501 SKEY BASE SPINDLE ... ORI FLOW DIM
        skey_name = (skey.name[:5]).ljust(5)
        base_name = (skey.name[:4]).ljust(4) # Often base is same as first 4 chars
        spindle_name = (skey.spindle_skey or "")[:4].ljust(4)

        orientation = str(skey.orientation).rjust(7)
        flow_arrow = str(skey.flow_arrow).rjust(7)
        dimensioned = str(skey.dimensioned).rjust(7)

        # 501 header with precise spacing for columns
        header = f"501  {skey_name} {base_name} {spindle_name}"
        header = header.ljust(30) + f"{orientation} {flow_arrow} {dimensioned}"
        lines = [header]

        # 2. Geometry 502
        # Convert standardized geometry strings to raw (Action, X, Y)
        # Using scale 20.0 (inverse of 0.05) and an offset of 50.0 to keep coords positive
        raw_geom = []
        offset_val = 50.0

        for item in skey.geometry:
            try:
                item_parts = item.split(":", 1)
                item_type = item_parts[0].strip()
                params_str = item_parts[1].strip()

                vals = {}
                for p in params_str.split(" "):
                    if "=" in p:
                        k, v = p.split("=")
                        vals[k] = float(v)

                if item_type in ("ArrivePoint", "LeavePoint", "TeePoint", "SpindlePoint"):
                    action = "1"
                    if item_type == "TeePoint": action = "3"
                    elif item_type == "SpindlePoint": action = "6"
                    raw_geom.append((action, round((vals["x0"] + offset_val) * 20.0, 1), round((vals["y0"] + offset_val) * 20.0, 1)))
                elif item_type == "Line":
                    raw_geom.append(("1", round((vals["x1"] + offset_val) * 20.0, 1), round((vals["y1"] + offset_val) * 20.0, 1)))
                    raw_geom.append(("2", round((vals["x2"] + offset_val) * 20.0, 1), round((vals["y2"] + offset_val) * 20.0, 1)))
                elif item_type == "Rectangle":
                    x, y, w, h = vals["x0"], vals["y0"], vals["width"], vals["height"]
                    rect_pts = [(x - w/2, y - h/2), (x + w/2, y - h/2), (x + w/2, y + h/2), (x - w/2, y + h/2), (x - w/2, y - h/2)]
                    for i, (px, py) in enumerate(rect_pts):
                        act = "1" if i == 0 else "2"
                        raw_geom.append((act, round((px + offset_val) * 20.0, 1), round((py + offset_val) * 20.0, 1)))
            except (ValueError, IndexError, KeyError):
                continue

        if not raw_geom:
            return "\n".join(lines)

        # 800 terminator
        raw_geom.append(("0", 0.0, 0.0))

        # Chunk into 502 records (up to 4 points per line)
        for i in range(0, len(raw_geom), 4):
            chunk = raw_geom[i:i+4]
            record = "502  "
            for act, rx, ry in chunk:
                # Format: Action(9) + Space(1) + X(7) + Space(1) + Y(7) + Space(1) = 26 chars
                # This matches the importer's positions 5, 31, 55, 79...
                record += f"{act.rjust(9)} {str(rx).rjust(7)} {str(ry).rjust(7)} "
            lines.append(record.rstrip())

        return "\n".join(lines)
