"""Save/replay compatibility checks for CompatX."""

from __future__ import annotations

from typing import Dict, Iterable, List


VALID_COMPATIBILITY_TYPES = {"forward", "backward", "full", "none"}


def validate_save_replay_entries(
    matrix_entries: Iterable[Dict[str, object]],
    migrations_by_id: Dict[str, Dict[str, object]],
) -> List[str]:
    errors: List[str] = []
    save_rows = []
    replay_rows = []

    for row in matrix_entries:
        component_type = str(row.get("component_type", "")).strip()
        if component_type == "save":
            save_rows.append(row)
        elif component_type == "replay":
            replay_rows.append(row)

    if not save_rows:
        errors.append("refuse.save_matrix_missing")
    if not replay_rows:
        errors.append("refuse.replay_matrix_missing")

    for row in save_rows + replay_rows:
        compatibility_type = str(row.get("compatibility_type", "")).strip()
        if compatibility_type not in VALID_COMPATIBILITY_TYPES:
            errors.append("refuse.save_replay_compatibility_type")
        migration_required = bool(row.get("migration_required", False))
        migration_id = str(row.get("migration_id", "")).strip()
        if migration_required:
            if not migration_id:
                errors.append("refuse.save_replay_migration_id")
            elif migration_id not in migrations_by_id:
                errors.append("refuse.save_replay_missing_migration")

    return sorted(set(errors))

