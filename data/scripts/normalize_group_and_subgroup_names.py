#!/usr/bin/env python3
"""Normalize group and subgroup spellings in the OpenIso SQLite database."""

from __future__ import annotations

import argparse
import sqlite3
from collections import defaultdict
from pathlib import Path


def _normalize_cluster_key(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", " ").replace("-", " ").split())


def _choose_canonical_variant(values: set[str], *, fallback: str | None = None) -> str:
    if not values:
        return fallback or ""

    def score(value: str) -> tuple[int, int, int, int, str]:
        text = value.strip()
        has_underscore = 0 if "_" in text else 1
        has_uppercase = 1 if any(char.isupper() for char in text) else 0
        has_punctuation = 1 if any(char in "-()" for char in text) else 0
        return (has_underscore, has_uppercase, has_punctuation, -len(text), text)

    return max(values, key=score)


def _sentence_case(value: str) -> str:
    normalized = " ".join(value.strip().replace("_", " ").split())
    if not normalized:
        return normalized
    lowered = normalized.lower()
    for index, char in enumerate(lowered):
        if char.isalpha():
            return lowered[:index] + char.upper() + lowered[index + 1 :]
    return lowered


def normalize_database(db_path: str | Path) -> dict[str, int]:
    database_path = Path(db_path)
    if not database_path.exists():
        raise FileNotFoundError(database_path)

    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = OFF")

        cur = conn.cursor()
        group_candidates: dict[str, set[str]] = defaultdict(set)
        subgroup_candidates: dict[tuple[str, str], set[str]] = defaultdict(set)

        def collect_pairs(table: str, group_column: str, subgroup_column: str | None = None) -> None:
            if subgroup_column is None:
                rows = cur.execute(f"SELECT {group_column} AS group_key FROM {table}").fetchall()
                for row in rows:
                    group_key = row["group_key"]
                    if group_key:
                        group_candidates[_normalize_cluster_key(group_key)].add(group_key)
                return

            rows = cur.execute(
                f"SELECT {group_column} AS group_key, {subgroup_column} AS subgroup_key FROM {table}"
            ).fetchall()
            for row in rows:
                group_key = row["group_key"]
                subgroup_key = row["subgroup_key"]
                if not group_key or not subgroup_key:
                    continue
                normalized_group = _normalize_cluster_key(group_key)
                normalized_subgroup = _normalize_cluster_key(subgroup_key)
                group_candidates[normalized_group].add(group_key)
                subgroup_candidates[(normalized_group, normalized_subgroup)].add(subgroup_key)

        collect_pairs("skey_groups", "skey_group_key")
        collect_pairs("skey_subgroups", "skey_group_key", "skey_subgroup_key")
        collect_pairs("skeys", "skey_group_key", "skey_subgroup_key")
        collect_pairs("spindles", "skey_group_key", "skey_subgroup_key")

        group_map: dict[str, str] = {}
        for normalized_group, values in group_candidates.items():
            canonical = _choose_canonical_variant(values, fallback=_sentence_case(normalized_group))
            group_map[normalized_group] = canonical

        subgroup_map: dict[tuple[str, str], str] = {}
        for normalized_key, values in subgroup_candidates.items():
            canonical = _choose_canonical_variant(values, fallback=_sentence_case(normalized_key[1]))
            subgroup_map[normalized_key] = canonical

        updated_skeys = 0
        updated_spindles = 0

        for row in cur.execute("SELECT id, skey_group_key, skey_subgroup_key FROM skeys").fetchall():
            normalized_group = _normalize_cluster_key(row["skey_group_key"])
            normalized_subgroup = _normalize_cluster_key(row["skey_subgroup_key"])
            new_group = group_map.get(normalized_group, row["skey_group_key"])
            new_subgroup = subgroup_map.get((normalized_group, normalized_subgroup), row["skey_subgroup_key"])
            if new_group != row["skey_group_key"] or new_subgroup != row["skey_subgroup_key"]:
                cur.execute(
                    "UPDATE skeys SET skey_group_key = ?, skey_subgroup_key = ? WHERE id = ?",
                    (new_group, new_subgroup, row["id"]),
                )
                updated_skeys += 1

        for row in cur.execute("SELECT id, skey_group_key, skey_subgroup_key FROM spindles").fetchall():
            normalized_group = _normalize_cluster_key(row["skey_group_key"])
            normalized_subgroup = _normalize_cluster_key(row["skey_subgroup_key"])
            new_group = group_map.get(normalized_group, row["skey_group_key"])
            new_subgroup = subgroup_map.get((normalized_group, normalized_subgroup), row["skey_subgroup_key"])
            if new_group != row["skey_group_key"] or new_subgroup != row["skey_subgroup_key"]:
                cur.execute(
                    "UPDATE spindles SET skey_group_key = ?, skey_subgroup_key = ? WHERE id = ?",
                    (new_group, new_subgroup, row["id"]),
                )
                updated_spindles += 1

        canonical_groups = sorted(set(group_map.values()))
        canonical_pairs = sorted(
            {
                (group_map[normalized_group], subgroup_map[(normalized_group, normalized_subgroup)])
                for normalized_group, normalized_subgroup in subgroup_map
            }
        )

        cur.execute("DELETE FROM skey_subgroups")
        cur.execute("DELETE FROM skey_groups")

        group_ids: dict[str, int] = {}
        for group_key in canonical_groups:
            cur.execute("INSERT INTO skey_groups (skey_group_key) VALUES (?)", (group_key,))
            group_ids[group_key] = int(cur.lastrowid)

        for group_key, subgroup_key in canonical_pairs:
            cur.execute(
                "INSERT INTO skey_subgroups (group_id, skey_group_key, skey_subgroup_key) VALUES (?, ?, ?)",
                (group_ids[group_key], group_key, subgroup_key),
            )

        conn.commit()

        foreign_key_issues = cur.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_key_issues:
            raise sqlite3.IntegrityError(f"Foreign key check failed: {foreign_key_issues}")

        return {
            "groups": len(canonical_groups),
            "subgroups": len(canonical_pairs),
            "skeys_updated": updated_skeys,
            "spindles_updated": updated_spindles,
        }
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "db_path",
        nargs="?",
        default=Path(__file__).resolve().parents[1] / "database" / "openiso.db",
        help="Path to the OpenIso SQLite database",
    )
    args = parser.parse_args()

    result = normalize_database(args.db_path)
    print(
        "Normalized database: "
        f"{result['groups']} groups, {result['subgroups']} subgroups, "
        f"{result['skeys_updated']} skeys, {result['spindles_updated']} spindles updated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())