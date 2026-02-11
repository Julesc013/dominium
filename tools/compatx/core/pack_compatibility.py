"""Pack, protocol, API, and ABI compatibility checks for CompatX."""

from __future__ import annotations

from typing import Dict, Iterable, List, Tuple


SUPPORTED_TYPES = {"pack", "protocol", "api", "abi"}
VALID_COMPATIBILITY_TYPES = {"forward", "backward", "full", "none"}


def validate_pack_entries(
    matrix_entries: Iterable[Dict[str, object]],
    migrations_by_id: Dict[str, Dict[str, object]],
) -> List[str]:
    errors: List[str] = []
    seen = set()
    any_supported = False

    for row in matrix_entries:
        component_type = str(row.get("component_type", "")).strip()
        if component_type not in SUPPORTED_TYPES:
            continue
        any_supported = True
        component_id = str(row.get("component_id", "")).strip()
        version_from = str(row.get("version_from", "")).strip()
        version_to = str(row.get("version_to", "")).strip()
        compatibility_type = str(row.get("compatibility_type", "")).strip()
        migration_required = bool(row.get("migration_required", False))
        migration_id = str(row.get("migration_id", "")).strip()

        key: Tuple[str, str, str, str] = (component_type, component_id, version_from, version_to)
        if key in seen:
            errors.append("refuse.pack_matrix_duplicate")
        seen.add(key)

        if compatibility_type not in VALID_COMPATIBILITY_TYPES:
            errors.append("refuse.pack_matrix_compatibility_type")
        if migration_required and migration_id and migration_id not in migrations_by_id:
            errors.append("refuse.pack_matrix_missing_migration")
        if migration_required and not migration_id:
            errors.append("refuse.pack_matrix_migration_id")

    if not any_supported:
        errors.append("refuse.pack_matrix_missing")
    return sorted(set(errors))


def validate_optional_bundle_removal(bundle_payload: Dict[str, object] | None) -> List[str]:
    if not isinstance(bundle_payload, dict):
        return []
    record = bundle_payload.get("record")
    if not isinstance(record, dict):
        return ["refuse.bundle_registry_record"]
    bundles = record.get("bundles")
    if not isinstance(bundles, list):
        return ["refuse.bundle_registry_bundles"]

    core_bundles = 0
    for row in bundles:
        if not isinstance(row, dict):
            continue
        bundle_id = str(row.get("bundle_id", "")).strip()
        optional = row.get("optional")
        if not bundle_id:
            return ["refuse.bundle_id_missing"]
        if not isinstance(optional, bool):
            return ["refuse.bundle_optional_flag"]
        if optional is False:
            core_bundles += 1

    if core_bundles < 1:
        return ["refuse.bundle_core_missing"]
    return []

