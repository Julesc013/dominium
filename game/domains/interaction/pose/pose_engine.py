"""Deterministic POSE-1 pose slot normalization and occupancy helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping


REFUSAL_POSE_OCCUPIED = "refusal.pose.occupied"
REFUSAL_POSE_NO_ACCESS_PATH = "refusal.pose.no_access_path"
REFUSAL_POSE_FORBIDDEN_BY_LAW = "refusal.pose.forbidden_by_law"
REFUSAL_POSE_INVALID_POSTURE = "refusal.pose.invalid_posture"
REFUSAL_POSE_NOT_OCCUPANT = "refusal.pose.not_occupant"


class PoseError(ValueError):
    """Deterministic pose refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _normalized_exclusivity(value: object) -> str:
    token = str(value).strip() or "single"
    if token not in {"single", "multiple"}:
        token = "single"
    return token


def _canonical_posture_id(value: object) -> str:
    token = str(value).strip()
    if not token:
        return ""
    if token.startswith("posture."):
        return token
    return "posture.{}".format(token)


def normalize_pose_slot_row(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    pose_slot_id = str(payload.get("pose_slot_id", "")).strip()
    parent_assembly_id = str(payload.get("parent_assembly_id", "")).strip()
    interior_volume_id = str(payload.get("interior_volume_id", "")).strip()
    if not pose_slot_id or not parent_assembly_id or not interior_volume_id:
        raise PoseError(
            REFUSAL_POSE_INVALID_POSTURE,
            "pose slot missing required identifiers",
            {
                "pose_slot_id": pose_slot_id,
                "parent_assembly_id": parent_assembly_id,
                "interior_volume_id": interior_volume_id,
            },
        )
    allowed_postures = []
    for token in _sorted_unique_strings(payload.get("allowed_postures")):
        canonical = _canonical_posture_id(token)
        if canonical:
            allowed_postures.append(canonical)
    allowed_body_tags = _sorted_unique_strings(payload.get("allowed_body_tags"))
    current_occupant = payload.get("current_occupant_id")
    current_occupant_id = None if current_occupant is None else str(current_occupant).strip() or None
    control_binding_raw = payload.get("control_binding_id")
    control_binding_id = None if control_binding_raw is None else str(control_binding_raw).strip() or None
    extensions = dict(payload.get("extensions") or {}) if isinstance(payload.get("extensions"), dict) else {}
    occupant_ids = _sorted_unique_strings(extensions.get("occupant_ids"))
    if current_occupant_id and current_occupant_id not in occupant_ids:
        occupant_ids.append(current_occupant_id)
    extensions["occupant_ids"] = _sorted_unique_strings(occupant_ids)
    return {
        "schema_version": "1.0.0",
        "pose_slot_id": pose_slot_id,
        "parent_assembly_id": parent_assembly_id,
        "interior_volume_id": interior_volume_id,
        "allowed_postures": list(allowed_postures),
        "allowed_body_tags": list(allowed_body_tags),
        "requires_access_path": bool(payload.get("requires_access_path", True)),
        "control_binding_id": control_binding_id,
        "exclusivity": _normalized_exclusivity(payload.get("exclusivity")),
        "current_occupant_id": current_occupant_id,
        "extensions": extensions,
    }


def normalize_pose_slot_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("pose_slot_id", ""))):
        normalized = normalize_pose_slot_row(row)
        out[str(normalized.get("pose_slot_id", ""))] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def pose_slot_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_pose_slot_rows(rows):
        out[str(row.get("pose_slot_id", ""))] = dict(row)
    return out


def control_binding_rows_by_id(control_binding_registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    root = dict(control_binding_registry_payload or {})
    rows = root.get("control_bindings")
    if not isinstance(rows, list):
        rows = (dict(root.get("record") or {})).get("control_bindings")
    if not isinstance(rows, list):
        return {}
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("control_binding_id", ""))):
        control_binding_id = str(row.get("control_binding_id", "")).strip()
        if not control_binding_id:
            continue
        out[control_binding_id] = {
            "schema_version": "1.0.0",
            "control_binding_id": control_binding_id,
            "grants_process_ids": _sorted_unique_strings(row.get("grants_process_ids")),
            "grants_surface_ids": _sorted_unique_strings(row.get("grants_surface_ids")),
            "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
        }
    return out


def _resolved_posture_id(pose_slot: Mapping[str, object], requested_posture: str) -> str:
    allowed_postures = _sorted_unique_strings((dict(pose_slot or {})).get("allowed_postures"))
    if not allowed_postures:
        return ""
    requested = _canonical_posture_id(requested_posture)
    if not requested:
        return str(allowed_postures[0])
    if requested in set(allowed_postures):
        return requested
    raise PoseError(
        REFUSAL_POSE_INVALID_POSTURE,
        "requested posture is not allowed for pose slot",
        {
            "pose_slot_id": str((dict(pose_slot or {})).get("pose_slot_id", "")).strip(),
            "requested_posture": requested,
            "allowed_postures": ",".join(allowed_postures),
        },
    )


def enter_pose_slot(
    *,
    pose_slot_row: Mapping[str, object],
    agent_id: str,
    requested_posture: str = "",
    override: bool = False,
) -> dict:
    pose_slot = normalize_pose_slot_row(pose_slot_row)
    agent_token = str(agent_id).strip()
    if not agent_token:
        raise PoseError(
            REFUSAL_POSE_INVALID_POSTURE,
            "pose_enter requires agent_id",
            {},
        )
    current_occupant_id = str(pose_slot.get("current_occupant_id") or "").strip()
    exclusivity = str(pose_slot.get("exclusivity", "")).strip() or "single"
    if exclusivity == "single" and current_occupant_id and current_occupant_id != agent_token and (not bool(override)):
        raise PoseError(
            REFUSAL_POSE_OCCUPIED,
            "pose slot is already occupied",
            {
                "pose_slot_id": str(pose_slot.get("pose_slot_id", "")),
                "current_occupant_id": current_occupant_id,
            },
        )
    posture_id = _resolved_posture_id(pose_slot, requested_posture)
    extensions = dict(pose_slot.get("extensions") or {})
    occupant_ids = _sorted_unique_strings(extensions.get("occupant_ids"))
    if exclusivity == "single":
        occupant_ids = [agent_token]
    else:
        if agent_token not in occupant_ids:
            occupant_ids.append(agent_token)
    extensions["occupant_ids"] = _sorted_unique_strings(occupant_ids)
    pose_slot["current_occupant_id"] = agent_token
    pose_slot["extensions"] = extensions
    return {
        "pose_slot": pose_slot,
        "posture_id": posture_id,
        "occupant_ids": _sorted_unique_strings(extensions.get("occupant_ids")),
    }


def exit_pose_slot(
    *,
    pose_slot_row: Mapping[str, object],
    agent_id: str,
    override: bool = False,
) -> dict:
    pose_slot = normalize_pose_slot_row(pose_slot_row)
    agent_token = str(agent_id).strip()
    if not agent_token:
        raise PoseError(
            REFUSAL_POSE_NOT_OCCUPANT,
            "pose_exit requires agent_id",
            {},
        )
    current_occupant_id = str(pose_slot.get("current_occupant_id") or "").strip()
    occupant_ids = _sorted_unique_strings((dict(pose_slot.get("extensions") or {})).get("occupant_ids"))
    if (not bool(override)) and agent_token not in set(occupant_ids + ([current_occupant_id] if current_occupant_id else [])):
        raise PoseError(
            REFUSAL_POSE_NOT_OCCUPANT,
            "agent is not currently occupying pose slot",
            {
                "pose_slot_id": str(pose_slot.get("pose_slot_id", "")),
                "agent_id": agent_token,
            },
        )
    remaining = [token for token in occupant_ids if token != agent_token]
    pose_slot["current_occupant_id"] = str(remaining[0]) if remaining else None
    ext = dict(pose_slot.get("extensions") or {})
    ext["occupant_ids"] = _sorted_unique_strings(remaining)
    pose_slot["extensions"] = ext
    return {
        "pose_slot": pose_slot,
        "remaining_occupant_ids": _sorted_unique_strings(remaining),
    }


def grants_for_subject(
    *,
    pose_slot_rows: object,
    subject_id: str,
    control_binding_registry_payload: Mapping[str, object] | None,
) -> dict:
    subject_token = str(subject_id).strip()
    if not subject_token:
        return {
            "control_binding_ids": [],
            "granted_process_ids": [],
            "granted_surface_ids": [],
            "pose_slot_ids": [],
        }
    slots = normalize_pose_slot_rows(pose_slot_rows)
    bindings = control_binding_rows_by_id(control_binding_registry_payload)
    control_binding_ids: List[str] = []
    granted_process_ids: List[str] = []
    granted_surface_ids: List[str] = []
    pose_slot_ids: List[str] = []
    for slot in sorted(slots, key=lambda item: str(item.get("pose_slot_id", ""))):
        slot_id = str(slot.get("pose_slot_id", "")).strip()
        current_occupant_id = str(slot.get("current_occupant_id") or "").strip()
        occupant_ids = _sorted_unique_strings((dict(slot.get("extensions") or {})).get("occupant_ids"))
        occupied = subject_token == current_occupant_id or subject_token in set(occupant_ids)
        if not occupied:
            continue
        pose_slot_ids.append(slot_id)
        binding_id = str(slot.get("control_binding_id", "")).strip()
        if not binding_id:
            continue
        binding_row = dict(bindings.get(binding_id) or {})
        if not binding_row:
            continue
        control_binding_ids.append(binding_id)
        granted_process_ids.extend(_sorted_unique_strings(binding_row.get("grants_process_ids")))
        granted_surface_ids.extend(_sorted_unique_strings(binding_row.get("grants_surface_ids")))
    return {
        "control_binding_ids": _sorted_unique_strings(control_binding_ids),
        "granted_process_ids": _sorted_unique_strings(granted_process_ids),
        "granted_surface_ids": _sorted_unique_strings(granted_surface_ids),
        "pose_slot_ids": _sorted_unique_strings(pose_slot_ids),
    }
