#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN
#
# Script to prepare en.po file for translation
# Since the source strings are in English, for English translation:
# - Remove fuzzy markers where msgstr matches msgid or is similar
# - Fill empty msgstr with msgid value (English -> English)
# - Clean up the file structure

import re
import sys
from pathlib import Path


def parse_po_entry(lines, start_idx):
    """Parse a single PO entry starting at the given index."""
    entry = {
        'start': start_idx,
        'comments': [],
        'msgid': '',
        'msgstr': '',
        'is_fuzzy': False,
        'flags': []
    }

    i = start_idx
    while i < len(lines):
        line = lines[i].rstrip()

        # Empty line marks end of entry
        if not line:
            entry['end'] = i
            return entry, i + 1

        # Comments and flags
        if line.startswith('#'):
            entry['comments'].append(line)
            if line.startswith('#, fuzzy'):
                entry['is_fuzzy'] = True
            elif line.startswith('#,'):
                entry['flags'].append(line)
            i += 1
            continue

        # msgid
        if line.startswith('msgid '):
            msgid = line[6:].strip('"')
            i += 1
            # Handle multi-line msgid
            while i < len(lines) and lines[i].startswith('"'):
                msgid += lines[i].strip().strip('"')
                i += 1
            entry['msgid'] = msgid
            continue

        # msgstr
        if line.startswith('msgstr '):
            msgstr = line[7:].strip('"')
            i += 1
            # Handle multi-line msgstr
            while i < len(lines) and lines[i].startswith('"'):
                msgstr += lines[i].strip().strip('"')
                i += 1
            entry['msgstr'] = msgstr
            continue

        i += 1

    entry['end'] = len(lines)
    return entry, len(lines)

def should_auto_translate(msgid, msgstr):
    """Determine if we should auto-fill English translation."""
    # Skip header entry
    if not msgid:
        return False

    # If msgstr is empty, auto-fill with msgid
    if not msgstr:
        return True

    # If msgstr is same as msgid, keep it (already correct)
    if msgstr == msgid:
        return False

    return False

def prepare_en_po(po_file_path):
    """Prepare en.po file for translation."""
    print(f"Processing {po_file_path}...")

    with open(po_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    output_lines = []
    i = 0
    entries_processed = 0
    fuzzy_removed = 0
    auto_filled = 0

    while i < len(lines):
        line = lines[i].rstrip()

        # Check if this is the start of an entry
        if line.startswith('#') or line.startswith('msgid '):
            entry, next_i = parse_po_entry(lines, i)

            if entry['msgid']:  # Not header
                entries_processed += 1

                # Remove fuzzy flag for English (source is already English)
                if entry['is_fuzzy']:
                    fuzzy_removed += 1
                    entry['is_fuzzy'] = False
                    entry['comments'] = [c for c in entry['comments'] if not c.startswith('#, fuzzy')]

                # Auto-fill empty translations for English
                if should_auto_translate(entry['msgid'], entry['msgstr']):
                    entry['msgstr'] = entry['msgid']
                    auto_filled += 1

                # Write the entry
                for comment in entry['comments']:
                    output_lines.append(comment + '\n')

                # Write msgid
                msgid = entry['msgid']
                if '\n' in msgid or len(msgid) > 70:
                    output_lines.append('msgid ""\n')
                    for part in msgid.split('\n'):
                        output_lines.append(f'"{part}\\n"\n')
                else:
                    output_lines.append(f'msgid "{msgid}"\n')

                # Write msgstr
                msgstr = entry['msgstr']
                if '\n' in msgstr or len(msgstr) > 70:
                    output_lines.append('msgstr ""\n')
                    for part in msgstr.split('\n'):
                        output_lines.append(f'"{part}\\n"\n')
                else:
                    output_lines.append(f'msgstr "{msgstr}"\n')

                output_lines.append('\n')
            else:
                # Header entry - keep as is
                for j in range(i, next_i):
                    output_lines.append(lines[j])

            i = next_i
        else:
            output_lines.append(lines[i])
            i += 1

    # Write back
    with open(po_file_path, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)

    print(f"✓ Processed {entries_processed} entries")
    print(f"✓ Removed {fuzzy_removed} fuzzy markers")
    print(f"✓ Auto-filled {auto_filled} empty translations")
    print(f"✓ File prepared: {po_file_path}")

if __name__ == '__main__':
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    po_file = project_root / 'po' / 'en.po'

    if not po_file.exists():
        print(f"Error: {po_file} not found")
        sys.exit(1)

    prepare_en_po(po_file)
    print("\nDone! The en.po file is now ready for translation.")
