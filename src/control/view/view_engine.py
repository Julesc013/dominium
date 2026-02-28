"""Deterministic CTRL-6 view binding engine."""

from __future__ import annotations

import fnmatch
from typing import Dict, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_VIEW_TARGET_INVALID = "refusal.view.target_invalid"
REFUSAL_VIEW_POLICY_FORBIDDEN = "refusal.view.mode_forbidden"
REFUSAL_VIEW_ENTITLEMENT_MISSING = "refusal.view.entitlement_missing"
REFUSAL_VIEW_REQUIRES_EMBODIMENT = "refusal.view.requires_embodiment"

_CAMERA_MODES = ("first_person", "third_person", "freecam", "spectator", "replay")


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda item: str(item)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _fingerprint(seed: Mapping[str, object]) -> str:
    return canonical_sha256(_canon(dict(seed or {})))


def _refusal(
    reason_code: str,
    message: str,
    remediation_hint: str,
    relevant_ids: Mapping[str, object] | None = None,
    path: str = "$",
) -> dict:
    ids = {}
    for key, value in sorted((_as_map(relevant_ids)).items(), key=lambda item: str(item[0])):
        token = str(value).strip()
        if token:
            ids[str(key)] = token
    return {
        "result": "refused",
        "refusal": {
            "reason_code": str(reason_code),
            "message": str(message),
            "remediation_hint": str(remediation_hint),
            "relevant_ids": ids,
            "path": str(path),
        },
        "errors": [{"code": str(reason_code), "message": str(message), "path": str(path)}],
    }


def normalize_view_binding_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: List[dict] = []
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("subject_id", ""))):
        subject_id = str(row.get("subject_id", "")).strip()
        current_view_policy_id = str(row.get("current_view_policy_id", "")).strip()
        if not subject_id or not current_view_policy_id:
            continue
        normalized = {
            "schema_version": "1.0.0",
            "subject_id": subject_id,
            "current_view_policy_id": current_view_policy_id,
            "bound_spatial_id": str(row.get("bound_spatial_id", "")).strip() or None,
            "bound_pose_slot_id": str(row.get("bound_pose_slot_id", "")).strip() or None,
            "created_tick": int(max(0, _as_int(row.get("created_tick", 0), 0))),
            "deterministic_fingerprint": "",
            "extensions": _as_map(row.get("extensions")),
        }
        seed = dict(normalized)
        seed["deterministic_fingerprint"] = ""
        normalized["deterministic_fingerprint"] = _fingerprint(seed)
        out.append(normalized)
    return sorted(out, key=lambda item: (str(item.get("subject_id", "")), str(item.get("current_view_policy_id", ""))))


def view_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("view_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("view_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("view_policy_id", ""))):
        view_policy_id = str(row.get("view_policy_id", "")).strip()
        camera_mode = str(row.get("camera_mode", "")).strip()
        if (not view_policy_id) or camera_mode not in _CAMERA_MODES:
            continue
        out[view_policy_id] = {
            "schema_version": "1.0.0",
            "view_policy_id": view_policy_id,
            "description": str(row.get("description", "")).strip(),
            "camera_mode": camera_mode,
            "allowed_epistemic_policy_ids": _sorted_unique_strings(row.get("allowed_epistemic_policy_ids")),
            "allowed_abstraction_levels": _sorted_unique_strings(row.get("allowed_abstraction_levels")),
            "restrictions": _as_map(row.get("restrictions")),
            "extensions": _as_map(row.get("extensions")),
        }
    return out


def _policy_mode(policy_row: Mapping[str, object]) -> str:
    mode = str(_as_map(policy_row).get("camera_mode", "")).strip()
    if mode in _CAMERA_MODES:
        return mode
    return "first_person"


def _legacy_view_mode_id(policy_row: Mapping[str, object]) -> str:
    ext = _as_map(_as_map(policy_row).get("extensions"))
    legacy_rows = _sorted_unique_strings(ext.get("legacy_view_mode_ids"))
    if legacy_rows:
        return legacy_rows[0]
    camera_mode = _policy_mode(policy_row)
    if camera_mode == "third_person":
        return "view.mode.third_person"
    if camera_mode == "freecam":
        return "view.mode.freecam"
    if camera_mode == "spectator":
        return "view.mode.spectator"
    if camera_mode == "replay":
        return "view.mode.replay"
    return "view.mode.first_person"


def resolve_view_policy_id(requested_id: str, policy_rows_by_id: Mapping[str, Mapping[str, object]]) -> str:
    requested = str(requested_id or "").strip()
    if not requested:
        return ""
    if requested in policy_rows_by_id:
        return requested
    for policy_id in sorted(policy_rows_by_id.keys()):
        policy = _as_map(policy_rows_by_id.get(policy_id))
        legacy_rows = _sorted_unique_strings(_as_map(policy.get("extensions")).get("legacy_view_mode_ids"))
        if requested in legacy_rows:
            return str(policy_id)
    return ""


def _allowed_policy_ids(
    *,
    policy_rows_by_id: Mapping[str, Mapping[str, object]],
    allowed_policy_patterns: Sequence[str],
) -> List[str]:
    patterns = _sorted_unique_strings(list(allowed_policy_patterns or []))
    if not patterns:
        return sorted(policy_rows_by_id.keys())
    out: List[str] = []
    for policy_id in sorted(policy_rows_by_id.keys()):
        row = _as_map(policy_rows_by_id.get(policy_id))
        legacy_rows = _sorted_unique_strings(_as_map(row.get("extensions")).get("legacy_view_mode_ids"))
        if any(fnmatch.fnmatch(policy_id, pattern) for pattern in patterns):
            out.append(policy_id)
            continue
        if any(any(fnmatch.fnmatch(legacy_id, pattern) for pattern in patterns) for legacy_id in legacy_rows):
            out.append(policy_id)
            continue
    return sorted(set(out))


def _first_policy_for_mode(
    *,
    policy_rows_by_id: Mapping[str, Mapping[str, object]],
    mode: str,
    allowed_policy_ids: Sequence[str],
) -> str:
    allowed = set(str(item).strip() for item in list(allowed_policy_ids or []) if str(item).strip())
    rows = [
        policy_id
        for policy_id in sorted(policy_rows_by_id.keys())
        if policy_id in allowed and _policy_mode(policy_rows_by_id[policy_id]) == str(mode)
    ]
    return rows[0] if rows else ""


def _downgrade_policy_id(
    *,
    requested_policy_id: str,
    policy_rows_by_id: Mapping[str, Mapping[str, object]],
    allowed_policy_ids: Sequence[str],
) -> str:
    mode = _policy_mode(policy_rows_by_id.get(str(requested_policy_id), {}))
    if mode == "freecam":
        for target_mode in ("third_person", "first_person"):
            token = _first_policy_for_mode(
                policy_rows_by_id=policy_rows_by_id,
                mode=target_mode,
                allowed_policy_ids=allowed_policy_ids,
            )
            if token:
                return token
    elif mode == "third_person":
        return _first_policy_for_mode(
            policy_rows_by_id=policy_rows_by_id,
            mode="first_person",
            allowed_policy_ids=allowed_policy_ids,
        )
    return ""


def apply_view_binding(
    *,
    subject_id: str,
    requested_view_policy_id: str,
    view_policy_registry: Mapping[str, object] | None,
    existing_view_bindings: object,
    created_tick: int,
    bound_spatial_id: str = "",
    bound_pose_slot_id: str = "",
    allowed_view_policy_patterns: Sequence[str] | None = None,
    entitlements: Sequence[str] | None = None,
    ranked_server: bool = False,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    subject_token = str(subject_id or "").strip()
    if not subject_token:
        return _refusal(
            REFUSAL_VIEW_TARGET_INVALID,
            "subject_id is required for process.view_bind",
            "Provide subject_id in process inputs.",
            {},
            "$.intent.inputs.subject_id",
        )
    policy_rows = view_policy_rows_by_id(view_policy_registry)
    if not policy_rows:
        return _refusal(
            REFUSAL_VIEW_POLICY_FORBIDDEN,
            "view policy registry payload is unavailable",
            "Load view_policy_registry before process.view_bind.",
            {},
            "$.navigation_indices.view_policy_registry",
        )

    requested_policy_id = resolve_view_policy_id(str(requested_view_policy_id), policy_rows)
    if not requested_policy_id:
        return _refusal(
            REFUSAL_VIEW_POLICY_FORBIDDEN,
            "requested view policy is not registered",
            "Use a view_policy_id present in view_policy_registry.",
            {"view_policy_id": str(requested_view_policy_id)},
            "$.intent.inputs.view_policy_id",
        )

    allowed_ids = _allowed_policy_ids(
        policy_rows_by_id=policy_rows,
        allowed_policy_patterns=list(allowed_view_policy_patterns or []),
    )
    if not allowed_ids:
        return _refusal(
            REFUSAL_VIEW_POLICY_FORBIDDEN,
            "active control policy does not allow any view policies",
            "Configure control policy allowed_view_policies for requested view access.",
            {},
            "$.control_policy.allowed_view_policies",
        )

    resolved_policy_id = str(requested_policy_id)
    downgrade_reason = ""
    if resolved_policy_id not in set(allowed_ids):
        fallback = _downgrade_policy_id(
            requested_policy_id=resolved_policy_id,
            policy_rows_by_id=policy_rows,
            allowed_policy_ids=allowed_ids,
        )
        if fallback:
            resolved_policy_id = fallback
            downgrade_reason = "downgrade.policy_disallows"
        else:
            return _refusal(
                REFUSAL_VIEW_POLICY_FORBIDDEN,
                "requested view policy is forbidden by active control policy",
                "Request an allowed view policy or elevate authority context.",
                {"requested_view_policy_id": requested_policy_id},
                "$.intent.inputs.view_policy_id",
            )

    if bool(ranked_server) and _policy_mode(policy_rows[resolved_policy_id]) == "freecam":
        fallback = _downgrade_policy_id(
            requested_policy_id=resolved_policy_id,
            policy_rows_by_id=policy_rows,
            allowed_policy_ids=allowed_ids,
        )
        if fallback:
            resolved_policy_id = fallback
            downgrade_reason = "downgrade.rank_fairness"
        else:
            return _refusal(
                REFUSAL_VIEW_POLICY_FORBIDDEN,
                "freecam view policy is forbidden in ranked server profile",
                "Use diegetic first-person or third-person view policy in ranked mode.",
                {"requested_view_policy_id": requested_policy_id},
                "$.intent.inputs.view_policy_id",
            )

    resolved_policy = _as_map(policy_rows.get(resolved_policy_id))
    restrictions = _as_map(resolved_policy.get("restrictions"))
    entitlement_rows = set(_sorted_unique_strings(list(entitlements or [])))
    if bool(restrictions.get("requires_observer_truth_entitlement", False)) and "entitlement.observer.truth" not in entitlement_rows:
        return _refusal(
            REFUSAL_VIEW_ENTITLEMENT_MISSING,
            "observer truth view policy requires entitlement.observer.truth",
            "Grant entitlement.observer.truth or choose non-observer view policy.",
            {"view_policy_id": resolved_policy_id},
            "$.authority_context.entitlements",
        )
    if bool(restrictions.get("requires_embodiment", False)) and (not str(bound_spatial_id).strip()) and (not str(bound_pose_slot_id).strip()):
        return _refusal(
            REFUSAL_VIEW_REQUIRES_EMBODIMENT,
            "requested view policy requires an embodied binding target",
            "Provide target_spatial_id or pose_slot_id for embodied view policy binding.",
            {"view_policy_id": resolved_policy_id},
            "$.intent.inputs",
        )

    binding_row = {
        "schema_version": "1.0.0",
        "subject_id": subject_token,
        "current_view_policy_id": resolved_policy_id,
        "bound_spatial_id": str(bound_spatial_id).strip() or None,
        "bound_pose_slot_id": str(bound_pose_slot_id).strip() or None,
        "created_tick": int(max(0, _as_int(created_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    seed = dict(binding_row)
    seed["deterministic_fingerprint"] = ""
    binding_row["deterministic_fingerprint"] = _fingerprint(seed)

    existing = normalize_view_binding_rows(existing_view_bindings)
    by_subject = dict((str(row.get("subject_id", "")), dict(row)) for row in existing)
    by_subject[subject_token] = dict(binding_row)
    normalized = [dict(by_subject[key]) for key in sorted(by_subject.keys()) if str(key).strip()]

    result = {
        "result": "complete",
        "view_bindings": normalized,
        "view_binding": dict(binding_row),
        "resolved_view_policy_id": resolved_policy_id,
        "resolved_legacy_view_mode_id": _legacy_view_mode_id(resolved_policy),
        "downgrade_reason": str(downgrade_reason),
    }
    if resolved_policy_id != requested_policy_id:
        result["downgraded_from"] = requested_policy_id
    return result


__all__ = [
    "REFUSAL_VIEW_ENTITLEMENT_MISSING",
    "REFUSAL_VIEW_POLICY_FORBIDDEN",
    "REFUSAL_VIEW_REQUIRES_EMBODIMENT",
    "REFUSAL_VIEW_TARGET_INVALID",
    "apply_view_binding",
    "normalize_view_binding_rows",
    "resolve_view_policy_id",
    "view_policy_rows_by_id",
]
