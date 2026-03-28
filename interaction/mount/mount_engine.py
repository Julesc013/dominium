"""Deterministic POSE-1 mount-point normalization and attach helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping


REFUSAL_MOUNT_INCOMPATIBLE = "refusal.mount.incompatible"
REFUSAL_MOUNT_ALREADY_ATTACHED = "refusal.mount.already_attached"
REFUSAL_MOUNT_FORBIDDEN_BY_LAW = "refusal.mount.forbidden_by_law"


class MountError(ValueError):
    """Deterministic mount refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def normalize_mount_point_row(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    mount_point_id = str(payload.get("mount_point_id", "")).strip()
    parent_assembly_id = str(payload.get("parent_assembly_id", "")).strip()
    state_machine_id = str(payload.get("state_machine_id", "")).strip()
    if not mount_point_id or not parent_assembly_id or not state_machine_id:
        raise MountError(
            REFUSAL_MOUNT_INCOMPATIBLE,
            "mount point missing required identifiers",
            {
                "mount_point_id": mount_point_id,
                "parent_assembly_id": parent_assembly_id,
                "state_machine_id": state_machine_id,
            },
        )
    return {
        "schema_version": "1.0.0",
        "mount_point_id": mount_point_id,
        "parent_assembly_id": parent_assembly_id,
        "mount_tags": _sorted_unique_strings(payload.get("mount_tags")),
        "alignment_constraints": dict(payload.get("alignment_constraints") or {}) if isinstance(payload.get("alignment_constraints"), dict) else {},
        "state_machine_id": state_machine_id,
        "connected_to_mount_point_id": (
            None
            if payload.get("connected_to_mount_point_id") is None
            else str(payload.get("connected_to_mount_point_id", "")).strip() or None
        ),
        "extensions": dict(payload.get("extensions") or {}) if isinstance(payload.get("extensions"), dict) else {},
    }


def normalize_mount_point_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("mount_point_id", ""))):
        normalized = normalize_mount_point_row(row)
        out[str(normalized.get("mount_point_id", ""))] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def mount_point_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_mount_point_rows(rows):
        out[str(row.get("mount_point_id", ""))] = dict(row)
    return out


def _compatible_mount_tags(a: Mapping[str, object], b: Mapping[str, object]) -> bool:
    a_tags = set(_sorted_unique_strings((dict(a or {})).get("mount_tags")))
    b_tags = set(_sorted_unique_strings((dict(b or {})).get("mount_tags")))
    if (not a_tags) or (not b_tags):
        return True
    return bool(a_tags.intersection(b_tags))


def _compatible_alignment(a: Mapping[str, object], b: Mapping[str, object]) -> bool:
    a_constraints = dict((dict(a or {})).get("alignment_constraints") or {})
    b_constraints = dict((dict(b or {})).get("alignment_constraints") or {})
    if not a_constraints or not b_constraints:
        return True
    a_profile = str(a_constraints.get("profile", "")).strip()
    b_profile = str(b_constraints.get("profile", "")).strip()
    if a_profile and b_profile and a_profile != b_profile:
        return False
    a_frame = str(a_constraints.get("frame_id", "")).strip()
    b_frame = str(b_constraints.get("frame_id", "")).strip()
    if a_frame and b_frame and a_frame != b_frame:
        return False
    return True


def _set_mount_state(row: dict, state_id: str) -> dict:
    ext = dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {}
    ext["state_id"] = str(state_id).strip() or "detached"
    row["extensions"] = ext
    return row


def attach_mount_points(
    *,
    mount_point_a_row: Mapping[str, object],
    mount_point_b_row: Mapping[str, object],
) -> dict:
    a_row = normalize_mount_point_row(mount_point_a_row)
    b_row = normalize_mount_point_row(mount_point_b_row)
    a_id = str(a_row.get("mount_point_id", "")).strip()
    b_id = str(b_row.get("mount_point_id", "")).strip()
    if not a_id or not b_id or a_id == b_id:
        raise MountError(
            REFUSAL_MOUNT_INCOMPATIBLE,
            "mount_attach requires two distinct mount points",
            {"mount_point_a_id": a_id, "mount_point_b_id": b_id},
        )
    a_connected = str(a_row.get("connected_to_mount_point_id") or "").strip()
    b_connected = str(b_row.get("connected_to_mount_point_id") or "").strip()
    if a_connected or b_connected:
        raise MountError(
            REFUSAL_MOUNT_ALREADY_ATTACHED,
            "mount point is already attached",
            {
                "mount_point_a_id": a_id,
                "mount_point_b_id": b_id,
                "current_a": a_connected,
                "current_b": b_connected,
            },
        )
    if not _compatible_mount_tags(a_row, b_row):
        raise MountError(
            REFUSAL_MOUNT_INCOMPATIBLE,
            "mount tags are incompatible",
            {
                "mount_point_a_id": a_id,
                "mount_point_b_id": b_id,
                "mount_tags_a": ",".join(_sorted_unique_strings(a_row.get("mount_tags"))),
                "mount_tags_b": ",".join(_sorted_unique_strings(b_row.get("mount_tags"))),
            },
        )
    if not _compatible_alignment(a_row, b_row):
        raise MountError(
            REFUSAL_MOUNT_INCOMPATIBLE,
            "alignment constraints are incompatible",
            {
                "mount_point_a_id": a_id,
                "mount_point_b_id": b_id,
            },
        )
    a_row["connected_to_mount_point_id"] = b_id
    b_row["connected_to_mount_point_id"] = a_id
    a_row = _set_mount_state(a_row, "attached")
    b_row = _set_mount_state(b_row, "attached")
    return {"mount_point_a": a_row, "mount_point_b": b_row}


def detach_mount_point(
    *,
    mount_point_row: Mapping[str, object],
) -> dict:
    row = normalize_mount_point_row(mount_point_row)
    connected_to = str(row.get("connected_to_mount_point_id") or "").strip()
    row["connected_to_mount_point_id"] = None
    row = _set_mount_state(row, "detached")
    return {"mount_point": row, "detached_from_mount_point_id": connected_to or None}
