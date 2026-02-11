"""Compatibility matrix loading and validation helpers for CompatX."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Iterable, List, Optional, Tuple


EXPECTED_SCHEMA_ID = "dominium.schema.governance.compat_matrix"
COMPATIBILITY_TYPES = {"forward", "backward", "full", "none"}
COMPONENT_TYPES = {"schema", "pack", "save", "replay", "protocol", "api", "abi", "identity"}


def _parse_semver(value: Any) -> Optional[Tuple[int, int, int]]:
    text = str(value or "").strip()
    parts = text.split(".")
    if len(parts) != 3:
        return None
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        return None


def load_json(path: str) -> Dict[str, Any] | None:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def validate_matrix_payload(payload: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
    errors: List[str] = []
    if str(payload.get("schema_id", "")).strip() != EXPECTED_SCHEMA_ID:
        errors.append("refuse.compat_matrix_schema_id")
    if _parse_semver(payload.get("schema_version")) is None:
        errors.append("refuse.compat_matrix_schema_version")

    record = payload.get("record")
    if not isinstance(record, dict):
        return [], sorted(set(errors + ["refuse.compat_matrix_record"]))

    entries = record.get("entries")
    if not isinstance(entries, list):
        return [], sorted(set(errors + ["refuse.compat_matrix_entries"]))

    seen_keys = set()
    normalized: List[Dict[str, Any]] = []
    for idx, row in enumerate(entries):
        if not isinstance(row, dict):
            errors.append("refuse.compat_matrix_entry_type")
            continue
        component_type = str(row.get("component_type", "")).strip()
        component_id = str(row.get("component_id", "")).strip()
        version_from = str(row.get("version_from", "")).strip()
        version_to = str(row.get("version_to", "")).strip()
        compatibility_type = str(row.get("compatibility_type", "")).strip()
        migration_required = row.get("migration_required")
        migration_id = str(row.get("migration_id", "")).strip()

        if component_type not in COMPONENT_TYPES:
            errors.append("refuse.compat_matrix_component_type")
        if not component_id:
            errors.append("refuse.compat_matrix_component_id")
        if _parse_semver(version_from) is None or _parse_semver(version_to) is None:
            errors.append("refuse.compat_matrix_version")
        if compatibility_type not in COMPATIBILITY_TYPES:
            errors.append("refuse.compat_matrix_compatibility_type")
        if not isinstance(migration_required, bool):
            errors.append("refuse.compat_matrix_migration_required")
        if migration_required and not migration_id:
            errors.append("refuse.compat_matrix_migration_id")

        key = (component_type, component_id, version_from, version_to)
        if key in seen_keys:
            errors.append("refuse.compat_matrix_duplicate")
            continue
        seen_keys.add(key)

        normalized.append(
            {
                "component_type": component_type,
                "component_id": component_id,
                "version_from": version_from,
                "version_to": version_to,
                "compatibility_type": compatibility_type,
                "migration_required": bool(migration_required),
                "migration_id": migration_id,
                "extensions": row.get("extensions", {}),
                "_index": idx,
            }
        )

    normalized.sort(
        key=lambda row: (
            row["component_type"],
            row["component_id"],
            row["version_from"],
            row["version_to"],
        )
    )
    return normalized, sorted(set(errors))


def build_matrix_index(entries: Iterable[Dict[str, Any]]) -> Dict[Tuple[str, str, str, str], Dict[str, Any]]:
    index: Dict[Tuple[str, str, str, str], Dict[str, Any]] = {}
    for row in entries:
        key = (
            str(row.get("component_type", "")).strip(),
            str(row.get("component_id", "")).strip(),
            str(row.get("version_from", "")).strip(),
            str(row.get("version_to", "")).strip(),
        )
        if all(key):
            index[key] = row
    return index


def transition_entry(
    index: Dict[Tuple[str, str, str, str], Dict[str, Any]],
    component_type: str,
    component_id: str,
    version_from: str,
    version_to: str,
) -> Dict[str, Any] | None:
    key = (
        str(component_type).strip(),
        str(component_id).strip(),
        str(version_from).strip(),
        str(version_to).strip(),
    )
    return index.get(key)


def validate_schema_policy_links(
    policy_entries: Iterable[Dict[str, Any]],
    matrix_entries: Iterable[Dict[str, Any]],
) -> List[str]:
    errors: List[str] = []
    matrix_ids = set()
    for row in matrix_entries:
        component_id = str(row.get("component_id", "")).strip()
        if component_id:
            matrix_ids.add(component_id)

    for row in policy_entries:
        schema_id = str(row.get("schema_id", "")).strip()
        if not schema_id:
            continue
        short_id = schema_id.rsplit(".", 1)[-1]
        if schema_id not in matrix_ids and short_id not in matrix_ids:
            errors.append("refuse.schema_policy_missing_matrix_link")
    return sorted(set(errors))
