#!/usr/bin/env python3
"""
Sync spindle names from IsoAlgo.skey file to database.
Compares ASC 501 records with DB and updates spindle_skey for symbols that have it in file but not in DB.
"""

import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openiso.controller.db import SkeyDB, DB_PATH
from openiso.core.app_context import resolve_data_dir


def parse_asc_501_records(file_path: str) -> dict[str, str]:
    """
    Parse IsoAlgo.skey file and extract symbol → spindle mappings from 501 records.
    ASC 501 format (fixed-width, 101 chars):
    - Positions 1-3: "501"
    - Positions 5-9: new field
    - Positions 11-15: base field (symbol code)
    - Positions 16-20: spindle field
    """
    mappings = {}

    with open(file_path, 'r') as f:
        for line in f:
            if not line.startswith(' 501'):
                continue

            # Extract fields from fixed positions (accounting for 0-based indexing)
            # Line format: " 501       CODE       SPINDLE  ..."
            symbol = line[10:15].strip()  # Positions 11-15 (0-indexed: 10-15)
            spindle = line[15:20].strip()  # Positions 16-20 (0-indexed: 15-20)

            if symbol:
                mappings[symbol] = spindle if spindle else None

    return mappings


def sync_spindle_names(db_path: str, asc_file: str) -> dict:
    """
    Compare IsoAlgo symbols with DB and update spindle_skey where needed.
    Returns: {
        'total_symbols_in_file': int,
        'symbols_in_db': int,
        'symbols_with_spindle_in_file': int,
        'updated': int,
        'no_spindle_needed': int,
        'symbol_not_found': int,
    }
    """
    # Parse file
    file_mappings = parse_asc_501_records(asc_file)
    print(f"📄 Parsed {len(file_mappings)} symbols from {asc_file}")

    # Open database
    db = SkeyDB(db_path)
    stats = {
        'total_symbols_in_file': len(file_mappings),
        'symbols_in_db': 0,
        'symbols_with_spindle_in_file': 0,
        'updated': 0,
        'no_spindle_needed': 0,
        'symbol_not_found': 0,
    }

    # Load all symbols from DB
    db_skeys = {skey.name: skey for skey in db.get_all_skeys()}
    stats['symbols_in_db'] = len(db_skeys)
    print(f"🗄️  Found {len(db_skeys)} symbols in database")

    # Process each symbol from file
    for symbol_name, spindle_name in file_mappings.items():
        if spindle_name is None:
            stats['no_spindle_needed'] += 1
            continue

        stats['symbols_with_spindle_in_file'] += 1

        if symbol_name not in db_skeys:
            stats['symbol_not_found'] += 1
            print(f"  ⚠️  Symbol '{symbol_name}' not found in DB")
            continue

        db_skey = db_skeys[symbol_name]

        # Check if spindle_skey is already set
        if db_skey.spindle_skey:
            # Already has spindle, skip
            continue

        # Need to update
        print(f"  ✏️  Updating '{symbol_name}' → spindle '{spindle_name}'")
        db_skey.spindle_skey = spindle_name
        db.update_skey(db_skey, user="sync_spindle_names", comment=f"Added spindle name from IsoAlgo.skey")
        stats['updated'] += 1

    return stats


def main():
    asc_file = Path(project_root) / "data" / "settings" / "IsoAlgo.skey"
    db_path = DB_PATH  # Uses resolve_data_dir()

    if not asc_file.exists():
        print(f"❌ File not found: {asc_file}")
        sys.exit(1)

    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)

    print(f"\n🔄 Syncing spindle names...")
    print(f"   File: {asc_file}")
    print(f"   DB:   {db_path}\n")

    stats = sync_spindle_names(db_path, str(asc_file))

    print(f"\n📊 Sync Results:")
    print(f"   Total symbols in file:        {stats['total_symbols_in_file']}")
    print(f"   Symbols in DB:                {stats['symbols_in_db']}")
    print(f"   Symbols with spindle in file: {stats['symbols_with_spindle_in_file']}")
    print(f"   Updated in DB:                {stats['updated']} ✅")
    print(f"   No spindle needed:            {stats['no_spindle_needed']}")
    print(f"   Symbol not found in DB:       {stats['symbol_not_found']}")
    print()


if __name__ == "__main__":
    main()
