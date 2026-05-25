import json
import os
import shutil

# Пути к файлам
FILE_PATH = '/home/rompik/Projects/Python/OpenIso/data/settings/OpenIso.json'
BACKUP_PATH = '/home/rompik/Projects/Python/OpenIso/data/settings/OpenIso_backup.json'

# Dictionary of replacements (SKEY -> [New Subgroup, New Description, New Group])
# All descriptions are translated into technical English
MAPPING = {
    # Valves & Instrumentation
    "ZV": ["Pressure Relief Valve", "Safety relief valve for pressure protection. Instrumentation type. ISO 14617-10.", "Valves"],
    "MA": ["Gate Valve (Manual)", "Manual gate valve for isolation. ASME B16.34 standard design.", "Valves"],
    "M3": ["3-Way Valve", "Three-way diverting/mixing valve. ISO 14617-4.", "Valves"],
    "M4": ["4-Way Valve", "Four-way crossover valve. ISO 14617-4.", "Valves"],
    "FI": ["Flow Indicator", "Sight flow indicator for visual process monitoring.", "Instrumentation"],
    "HV": ["Hand Valve", "Generic manual isolation valve. Handwheel or lever operated.", "Valves"],
    "HA": ["Valve Actuator", "Generic valve actuator symbol.", "Valves"],

    # Fittings & Flanges
    "COSW": ["Socket Weld Coupling", "Full coupling, socket weld (SW) type. ASME B16.11.", "Fittings"],
    "FLSJ": ["Lap Joint Flange", "Lap joint flange for use with stub ends. ASME B16.5.", "Flanges"],
    "FLWN": ["Weld Neck Flange", "Tapered hub flange for butt welding. ASME B16.5.", "Flanges"],
    "FLBL": ["Blind Flange", "Flange used to seal the end of a piping system. ASME B16.5.", "Flanges"],
    "KASW": ["Socket Weld Cap", "Pipe cap, socket weld (SW) connection. ASME B16.11.", "Fittings"],
    "NI": ["Swage Nipple (BW)", "Concentric swage nipple, butt weld (BW) ends. ASME B16.9.", "Reducers"],
    "CTBW": ["Concentric Reducer", "Concentric reducer, butt weld. ASME B16.9 / ISO 5251.", "Reducers"],
    "REBW": ["Eccentric Reducer", "Eccentric reducer for horizontal line drainage. ASME B16.9.", "Reducers"],

    # Supports & Misc
    "HANG": ["Pipe Hanger", "Rigid pipe hanger support for vertical loads.", "Supports"],
    "MP": ["Magnetic Flowmeter", "Electromagnetic flow meter. Process instrumentation.", "Instrumentation"],
    "II": ["Insulating Joint", "Dielectric insulation kit/gasket for corrosion protection.", "Fittings"],
    "WELD": ["Weld Point", "Field or shop weld identification mark.", "Welds"],

    # Spindles (Operators)
    "01SP": ["Standard Handwheel", "Manual handwheel valve operator.", "Spindles"],
    "02SP": ["Lever Operator", "Manual lever/handle for quarter-turn valves.", "Spindles"],
    "10SP": ["Chain Wheel", "Chain operated handwheel for high-reach valves.", "Spindles"],
    "11SP": ["Electric Actuator", "Motor-operated valve (MOV) electric actuator.", "Spindles"],
    "12SP": ["Pneumatic Actuator", "Air-operated valve (AOV) pneumatic actuator.", "Spindles"],
}

def clean_and_translate_library(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    # Create backup
    shutil.copy2(file_path, BACKUP_PATH)
    print(f"Backup created: {BACKUP_PATH}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_count = 0

    for skey, params in data.items():
        # 1. Update from mapping
        if skey in MAPPING:
            new_sub, new_desc, new_group = MAPPING[skey]
            params['subgroup'] = new_sub
            params['description'] = new_desc
            params['skey_group'] = new_group
            updated_count += 1

        # 2. General cleanup for remaining Unknowns
        else:
            if params.get('subgroup') == 'Unknown':
                params['subgroup'] = 'Generic Fitting'

            if params.get('skey_group') == 'Unknown':
                params['skey_group'] = 'Miscellaneous'

            if params.get('description') == "":
                params['description'] = f"Symbol SKEY: {skey}. Technical specification pending."

            # Translate 'All' to English if present
            if params.get('subgroup') == 'Все' or params.get('subgroup') == 'All':
                params['subgroup'] = 'Universal'

            updated_count += 1

    # Save the English version
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Success! Updated and translated {updated_count} elements.")

if __name__ == "__main__":
    clean_and_translate_library(FILE_PATH)