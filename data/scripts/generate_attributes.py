import json
import os
import shutil

# Paths
FILE_PATH = '/home/rompik/Projects/Python/OpenIso/data/settings/OpenIso.json'
BACKUP_PATH = '/home/rompik/Projects/Python/OpenIso/data/settings/OpenIso_backup_attributes.json'

# Knowledge base for components
SPINDLES_GROUP = 'Spindles'

def extract_connection_type(description, subgroup, skey):
    """Extract connection type from description or SKEY"""
    desc_lower = description.lower() if description else ""

    if 'butt weld' in desc_lower or 'BW' in skey:
        return 'BW'
    elif 'socket weld' in desc_lower or 'SW' in skey:
        return 'SW'
    elif 'threaded' in desc_lower or 'THD' in skey:
        return 'THD'
    elif 'flange' in desc_lower or 'FL' in skey or 'FLG' in skey:
        return 'FLG'
    elif 'clamp' in desc_lower or 'CL' in skey or 'clamp' in subgroup.lower():
        return 'PL'
    else:
        return 'None'

def extract_standard(description):
    """Extract standard from description"""
    if not description:
        return 'None'

    if 'ASME B16.5' in description:
        return 'ASME B16.5'
    elif 'ASME B16.9' in description:
        return 'ASME B16.9'
    elif 'ASME B16.34' in description:
        return 'ASME B16.34'
    elif 'ASME B16.11' in description:
        return 'ASME B16.11'
    elif 'ISO 14617' in description:
        return 'ISO 14617'
    elif 'ISO 5251' in description:
        return 'ISO 5251'
    elif 'ISO 1219' in description:
        return 'ISO 1219'
    else:
        return 'ISO 14617'

def determine_component_function(skey_group, subgroup, description):
    """Determine the primary function of the component"""
    group_lower = skey_group.lower() if skey_group else ""
    subgroup_lower = subgroup.lower() if subgroup else ""
    desc_lower = description.lower() if description else ""

    if 'spindle' in group_lower or 'operator' in group_lower:
        return 'Operator'
    elif 'safety' in desc_lower or 'relief' in desc_lower:
        return 'Safety'
    elif 'flow' in desc_lower or 'throttle' in desc_lower or 'regulation' in desc_lower:
        return 'Regulation'
    elif 'valve' in group_lower and ('isolation' in desc_lower or 'gate' in desc_lower or 'ball' in desc_lower):
        return 'Isolation'
    elif 'valve' in group_lower:
        return 'Isolation'
    elif 'flange' in group_lower or 'fitting' in group_lower or 'coupling' in group_lower or 'reducer' in group_lower:
        return 'Joining'
    elif 'support' in group_lower or 'hanger' in group_lower or 'anchor' in group_lower:
        return 'Support'
    else:
        return 'Joining'

def determine_is_pressure_part(skey_group, component_function):
    """Determine if this is a pressure-containing part"""
    if component_function == 'Operator':
        return False
    elif 'support' in skey_group.lower() or 'penetration' in skey_group.lower():
        return False
    else:
        return True

def get_compatible_spindles(skey, subgroup, description, spindle_skey):
    """Determine which spindles can be attached to this component"""
    compatible = []

    if spindle_skey and spindle_skey.strip():
        compatible.append(spindle_skey)

    desc_lower = description.lower() if description else ""

    if 'gate valve' in desc_lower or 'ball valve' in desc_lower or 'butterfly' in desc_lower:
        if spindle_skey not in ['01SP', '11SP']:
            compatible.extend(['01SP', '11SP'])
    elif 'quarter-turn' in desc_lower or 'lever' in desc_lower:
        if spindle_skey not in ['02SP', '12SP']:
            compatible.extend(['02SP', '12SP'])
    elif 'high-reach' in desc_lower or 'chain' in desc_lower:
        if '10SP' not in compatible:
            compatible.append('10SP')

    return list(set(compatible))

def determine_spindle_type(skey, description, spindle_skey):
    """Determine the spindle type for valves"""
    desc_lower = description.lower() if description else ""

    if skey == 'ZV':
        return 'Automatic'

    if spindle_skey and spindle_skey.strip():
        if 'SP' in spindle_skey:
            if '01' in spindle_skey:
                return 'Manual_Handwheel'
            elif '02' in spindle_skey:
                return 'Lever'
            elif '10' in spindle_skey:
                return 'Gear'
            elif '11' in spindle_skey:
                return 'Actuator'
            elif '12' in spindle_skey:
                return 'Actuator'

    if 'handwheel' in desc_lower or 'manual handwheel' in desc_lower:
        return 'Manual_Handwheel'
    elif 'lever' in desc_lower:
        return 'Lever'
    elif 'chain' in desc_lower:
        return 'Gear'
    elif 'actuator' in desc_lower or 'motor' in desc_lower or 'pneumatic' in desc_lower:
        return 'Actuator'
    elif 'relief' in desc_lower or 'safety' in desc_lower:
        return 'Automatic'

    return None

def get_operator_interface(skey, subgroup):
    """For spindle components, determine the interface type"""
    subgroup_lower = subgroup.lower() if subgroup else ""

    if 'handwheel' in subgroup_lower:
        return 'Stem_Mount'
    elif 'lever' in subgroup_lower or 'hand' in subgroup_lower:
        return 'Yoke'
    elif 'chain' in subgroup_lower:
        return 'Top_Flange'
    elif 'electric' in subgroup_lower or 'actuator' in subgroup_lower:
        return 'Top_Flange'
    elif 'pneumatic' in subgroup_lower:
        return 'Top_Flange'

    return 'Stem_Mount'

def generate_pcf_identification(skey, skey_group, component_function):
    """Generate PCF (Piping Component Function) Identification"""
    # Format: GROUP_SKEY_FUNC
    group_abbr = skey_group[:3].upper() if skey_group else 'UNK'
    func_abbr = component_function[:3].upper() if component_function else 'UNK'
    return f"{group_abbr}_{skey}_{func_abbr}"

def generate_idf_record(skey):
    """Generate IDF (Identifier/Definition) Record numbers"""
    # Generate numeric identifiers based on SKEY hash
    # Returns array of numbers (1-3 values)
    hash_val = sum(ord(c) for c in skey)
    idf_records = [hash_val % 10000, (hash_val * 7) % 10000, (hash_val * 13) % 10000]
    # Remove duplicates and keep 1-3 values
    return sorted(list(set(idf_records)))[:3]

def generate_attributes(skey, item, all_data):
    """Generate comprehensive attributes for a single SKEY"""

    # Preserve existing attributes if they exist
    if 'attributes' in item:
        existing_attrs = item['attributes'].copy()
    else:
        existing_attrs = {}

    subgroup = item.get('subgroup', '')
    description = item.get('description', '')
    skey_group = item.get('skey_group', '')
    spindle_skey = item.get('spindle_skey', '')

    is_spindle = skey_group.lower() == SPINDLES_GROUP.lower()

    # Build attributes
    attributes = {
        'connection_type': existing_attrs.get('connection_type') or extract_connection_type(description, subgroup, skey),
        'standard': existing_attrs.get('standard') or extract_standard(description),
        'component_function': existing_attrs.get('component_function') or determine_component_function(skey_group, subgroup, description),
        'is_pressure_part': existing_attrs.get('is_pressure_part') if 'is_pressure_part' in existing_attrs else determine_is_pressure_part(skey_group, determine_component_function(skey_group, subgroup, description)),
    }

    # Spindle/Actuator specific logic
    component_func = attributes['component_function']

    if is_spindle:
        attributes['is_pressure_part'] = False
        attributes['component_function'] = 'Operator'
        attributes['requires_spindle'] = False
        attributes['operator_interface'] = existing_attrs.get('operator_interface') or get_operator_interface(skey, subgroup)
    else:
        # Determine if requires spindle
        requires_spindle = component_func in ['Isolation', 'Regulation', 'Safety'] or (spindle_skey and spindle_skey.strip() != '')
        if 'requires_spindle' in existing_attrs:
            attributes['requires_spindle'] = existing_attrs['requires_spindle']
        else:
            attributes['requires_spindle'] = requires_spindle

        if attributes['requires_spindle']:
            attributes['spindle_type'] = existing_attrs.get('spindle_type') or determine_spindle_type(skey, description, spindle_skey)
            attributes['compatible_spindles'] = existing_attrs.get('compatible_spindles') or get_compatible_spindles(skey, subgroup, description, spindle_skey)

    # Add new attributes: PCF Identification and IDF Record
    attributes['pcf_identification'] = existing_attrs.get('pcf_identification') or generate_pcf_identification(skey, skey_group, attributes['component_function'])
    attributes['idf_record'] = existing_attrs.get('idf_record') or generate_idf_record(skey)

    return attributes

def process_library(file_path):
    """Process the entire library and add attributes"""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    # Create backup
    shutil.copy2(file_path, BACKUP_PATH)
    print(f"Backup created: {BACKUP_PATH}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_count = 0

    for skey, item in data.items():
        try:
            attributes = generate_attributes(skey, item, data)
            item['attributes'] = attributes
            updated_count += 1
        except Exception as e:
            print(f"Error processing {skey}: {e}")

    # Save the updated file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"\n✓ Success! Generated attributes for {updated_count} SKEYs")

    # Print statistics
    spindles_count = sum(1 for item in data.values() if item.get('attributes', {}).get('component_function') == 'Operator')
    pressure_parts = sum(1 for item in data.values() if item.get('attributes', {}).get('is_pressure_part'))
    requires_spindle = sum(1 for item in data.values() if item.get('attributes', {}).get('requires_spindle'))

    print(f"  - Spindles/Operators: {spindles_count}")
    print(f"  - Pressure-containing parts: {pressure_parts}")
    print(f"  - Components requiring spindles: {requires_spindle}")
    print(f"  - New attributes added: pcf_identification, idf_record")

if __name__ == "__main__":
    process_library(FILE_PATH)
