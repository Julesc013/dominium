"""Migration registry validation and deterministic migration execution for CompatX."""

from __future__ import annotations

import copy
import hashlib
import json
import os
from typing import Any, Dict, Iterable, List, Tuple


EXPECTED_SCHEMA_ID = "dominium.schema.governance.migration_spec"  # schema_version: 1.0.0


def _parse_semver(value: Any) -> Tuple[int, int, int] | None:
    parts = str(value or "").strip().split(".")
    if len(parts) != 3:
        return None
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        return None


def _load_json(path: str) -> Dict[str, Any] | None:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _canonical_sha(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def load_migration_payload(path: str) -> Dict[str, Any] | None:
    return _load_json(path)


def validate_migration_payload(payload: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
    errors: List[str] = []
    if str(payload.get("schema_id", "")).strip() != EXPECTED_SCHEMA_ID:
        errors.append("refuse.migration_schema_id")
    if _parse_semver(payload.get("schema_version")) is None:
        errors.append("refuse.migration_schema_version")

    record = payload.get("record")
    if not isinstance(record, dict):
        return [], sorted(set(errors + ["refuse.migration_record"]))
    rows = record.get("migrations")
    if not isinstance(rows, list):
        return [], sorted(set(errors + ["refuse.migration_rows"]))

    normalized: List[Dict[str, Any]] = []
    seen_ids = set()
    for row in rows:
        if not isinstance(row, dict):
            errors.append("refuse.migration_row_type")
            continue
        migration_id = str(row.get("migration_id", "")).strip()
        from_version = str(row.get("from_version", "")).strip()
        to_version = str(row.get("to_version", "")).strip()
        component_type = str(row.get("component_type", "")).strip()
        migration_tool = str(row.get("migration_tool", "")).strip()
        deterministic_required = row.get("deterministic_required")

        if not migration_id:
            errors.append("refuse.migration_id_missing")
            continue
        if migration_id in seen_ids:
            errors.append("refuse.migration_id_duplicate")
            continue
        seen_ids.add(migration_id)
        if _parse_semver(from_version) is None or _parse_semver(to_version) is None:
            errors.append("refuse.migration_version_invalid")
        if not component_type:
            errors.append("refuse.migration_component_type_missing")
        if not migration_tool:
            errors.append("refuse.migration_tool_missing")
        if not isinstance(deterministic_required, bool):
            errors.append("refuse.migration_deterministic_flag")

        normalized.append(
            {
                "migration_id": migration_id,
                "from_version": from_version,
                "to_version": to_version,
                "component_type": component_type,
                "deterministic_required": bool(deterministic_required),
                "migration_tool": migration_tool,
                "notes": row.get("notes", ""),
                "version_field": str(row.get("version_field", "")).strip(),
            }
        )

    normalized.sort(key=lambda row: row["migration_id"])
    return normalized, sorted(set(errors))


def migration_index(rows: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        migration_id = str(row.get("migration_id", "")).strip()
        if migration_id:
            index[migration_id] = row
    return index


def validate_matrix_coverage(matrix_entries: Iterable[Dict[str, Any]], migration_ids: Iterable[str]) -> List[str]:
    available = set(str(item).strip() for item in migration_ids if str(item).strip())
    errors: List[str] = []
    for row in matrix_entries:
        if not bool(row.get("migration_required", False)):
            continue
        migration_id = str(row.get("migration_id", "")).strip()
        if not migration_id:
            errors.append("refuse.compat_matrix_migration_id")
            continue
        if migration_id not in available:
            errors.append("refuse.compat_matrix_missing_migration")
    return sorted(set(errors))


def apply_migration(payload: Dict[str, Any], migration: Dict[str, Any]) -> Dict[str, Any]:
    output = copy.deepcopy(payload)
    version_field = str(migration.get("version_field", "")).strip() or "schema_version"
    output[version_field] = str(migration.get("to_version", "")).strip()
    output.setdefault("migration_history", [])
    history_row = {
        "migration_id": str(migration.get("migration_id", "")).strip(),
        "from_version": str(migration.get("from_version", "")).strip(),
        "to_version": str(migration.get("to_version", "")).strip(),
    }
    history = output.get("migration_history")
    if isinstance(history, list):
        if history_row not in history:
            history.append(history_row)
        history.sort(key=lambda row: str(row.get("migration_id", "")))
    return output


def run_migration(payload: Dict[str, Any], migration: Dict[str, Any]) -> Dict[str, Any]:
    migrated = apply_migration(payload, migration)
    return {
        "ok": True,
        "migration_id": str(migration.get("migration_id", "")).strip(),
        "result": migrated,
        "result_sha256": _canonical_sha(migrated),
    }


def load_and_validate(path: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    payload = load_migration_payload(path)
    if payload is None:
        return [], ["refuse.migration_registry_missing"]
    return validate_migration_payload(payload)


def migration_tool_exists(repo_root: str, migration_tool: str) -> bool:
    value = str(migration_tool or "").strip()
    if not value:
        return False
    rel = value.split("::", 1)[0]
    candidate = os.path.join(repo_root, rel.replace("/", os.sep))
    return os.path.isfile(candidate)
