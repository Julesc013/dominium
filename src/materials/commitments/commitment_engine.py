"""Deterministic MAT-8 commitment + reenactment helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_COMMITMENT_REQUIRED_MISSING = "refusal.commitment.required_missing"
REFUSAL_COMMITMENT_FORBIDDEN = "refusal.commitment.forbidden"
REFUSAL_COMMITMENT_INVALID_SCHEDULE = "refusal.commitment.invalid_schedule"
REFUSAL_REENACTMENT_BUDGET_EXCEEDED = "refusal.reenactment.budget_exceeded"
REFUSAL_REENACTMENT_FORBIDDEN_BY_LAW = "refusal.reenactment.forbidden_by_law"

_VALID_COMMITMENT_STATUSES = {
    "planned",
    "scheduled",
    "executing",
    "completed",
    "failed",
    "cancelled",
}
_MAJOR_CHANGE_PROCESS_IDS = {
    "process.manifest_create",
    "process.manifest_tick",
    "process.construction_project_create",
    "process.construction_project_tick",
    "process.maintenance_schedule",
    "process.maintenance_perform",
}


class CommitmentError(ValueError):
    """Deterministic commitment/reenactment refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _row_fingerprint(row: Mapping[str, object]) -> str:
    seed = dict(row or {})
    seed["deterministic_fingerprint"] = ""
    return canonical_sha256(seed)


def normalize_commitment_row(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    commitment_id = str(payload.get("commitment_id", "")).strip()
    commitment_type_id = str(payload.get("commitment_type_id", "")).strip()
    target_kind = str(payload.get("target_kind", "")).strip() or "custom"
    target_id = str(payload.get("target_id", "")).strip()
    if not commitment_id or not commitment_type_id or not target_id:
        raise CommitmentError(
            REFUSAL_COMMITMENT_INVALID_SCHEDULE,
            "commitment row is missing deterministic identity fields",
            {
                "commitment_id": commitment_id,
                "commitment_type_id": commitment_type_id,
                "target_id": target_id,
            },
        )
    status = str(payload.get("status", "planned")).strip() or "planned"
    if status not in _VALID_COMMITMENT_STATUSES:
        status = "planned"
    scheduled_start_tick = max(0, _as_int(payload.get("scheduled_start_tick", 0), 0))
    scheduled_end_raw = payload.get("scheduled_end_tick")
    scheduled_end_tick = None
    if scheduled_end_raw is not None:
        scheduled_end_tick = max(0, _as_int(scheduled_end_raw, 0))
        if int(scheduled_end_tick) < int(scheduled_start_tick):
            raise CommitmentError(
                REFUSAL_COMMITMENT_INVALID_SCHEDULE,
                "scheduled_end_tick must be >= scheduled_start_tick",
                {
                    "commitment_id": commitment_id,
                    "scheduled_start_tick": int(scheduled_start_tick),
                    "scheduled_end_tick": int(scheduled_end_tick),
                },
            )
    out = {
        "schema_version": "1.0.0",
        "commitment_id": commitment_id,
        "commitment_type_id": commitment_type_id,
        "actor_subject_id": str(payload.get("actor_subject_id", "")).strip() or "subject.system",
        "target_kind": target_kind,
        "target_id": target_id,
        "created_tick": max(0, _as_int(payload.get("created_tick", 0), 0)),
        "scheduled_start_tick": int(scheduled_start_tick),
        "scheduled_end_tick": scheduled_end_tick,
        "required_inputs": _sorted_unique_strings(payload.get("required_inputs")),
        "expected_outputs": _sorted_unique_strings(payload.get("expected_outputs")),
        "status": status,
        "linked_project_id": (
            None if payload.get("linked_project_id") is None else str(payload.get("linked_project_id", "")).strip() or None
        ),
        "linked_manifest_id": (
            None if payload.get("linked_manifest_id") is None else str(payload.get("linked_manifest_id", "")).strip() or None
        ),
        "linked_event_ids": _sorted_unique_strings(payload.get("linked_event_ids")),
        "deterministic_fingerprint": "",
        "extensions": dict(payload.get("extensions") or {}),
    }
    out["deterministic_fingerprint"] = _row_fingerprint(out)
    return out


def normalize_commitment_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("commitment_id", ""))):
        commitment_id = str(row.get("commitment_id", "")).strip()
        if not commitment_id:
            continue
        try:
            out[commitment_id] = normalize_commitment_row(row)
        except CommitmentError:
            continue
    return [dict(out[key]) for key in sorted(out.keys())]


def commitment_type_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    root = dict(registry_payload or {})
    rows = root.get("commitment_types")
    if not isinstance(rows, list):
        rows = ((root.get("record") or {}).get("commitment_types") or [])
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("commitment_type_id", ""))):
        commitment_type_id = str(row.get("commitment_type_id", "")).strip()
        if not commitment_type_id:
            continue
        out[commitment_type_id] = {
            "schema_version": "1.0.0",
            "commitment_type_id": commitment_type_id,
            "description": str(row.get("description", "")).strip(),
            "required_entitlements": _sorted_unique_strings(row.get("required_entitlements")),
            "produces_event_type_ids": _sorted_unique_strings(row.get("produces_event_type_ids")),
            "strictness_requirements": _sorted_unique_strings(row.get("strictness_requirements")),
            "extensions": dict(row.get("extensions") or {}),
        }
    return out


def causality_strictness_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    root = dict(registry_payload or {})
    rows = root.get("strictness_levels")
    if not isinstance(rows, list):
        rows = ((root.get("record") or {}).get("strictness_levels") or [])
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("causality_strictness_id", ""))):
        strictness_id = str(row.get("causality_strictness_id", "")).strip()
        if not strictness_id:
            continue
        out[strictness_id] = {
            "schema_version": "1.0.0",
            "causality_strictness_id": strictness_id,
            "level": str(row.get("level", "")).strip() or "C0",
            "description": str(row.get("description", "")).strip(),
            "major_change_requires_commitment": bool(row.get("major_change_requires_commitment", False)),
            "event_required_for_macro_change": bool(row.get("event_required_for_macro_change", True)),
            "extensions": dict(row.get("extensions") or {}),
        }
    return out


def resolve_causality_strictness_row(
    *,
    policy_context: Mapping[str, object] | None,
    strictness_registry_payload: Mapping[str, object] | None,
) -> dict:
    strictness_rows = causality_strictness_rows_by_id(strictness_registry_payload)
    policy = dict(policy_context or {})
    strictness_id = str(policy.get("causality_strictness_id", "")).strip()
    if not strictness_id:
        physics_profile = dict(policy.get("selected_physics_profile") or {})
        extensions = dict(physics_profile.get("extensions") or {})
        strictness_id = str(extensions.get("default_causality_strictness_id", "")).strip()
    if not strictness_id:
        strictness_id = "causality.C0"
    row = dict(strictness_rows.get(strictness_id) or {})
    if row:
        return row
    fallback = dict(strictness_rows.get("causality.C0") or {})
    if fallback:
        return fallback
    return {
        "schema_version": "1.0.0",
        "causality_strictness_id": "causality.C0",
        "level": "C0",
        "description": "default fallback",
        "major_change_requires_commitment": False,
        "event_required_for_macro_change": True,
        "extensions": {"fallback": True},
    }


def strictness_requires_commitment(*, process_id: str, strictness_row: Mapping[str, object] | None) -> bool:
    row = dict(strictness_row or {})
    if str(process_id).strip() not in _MAJOR_CHANGE_PROCESS_IDS:
        return False
    return bool(row.get("major_change_requires_commitment", False))


def create_commitment_row(
    *,
    commitment_type_id: str,
    actor_subject_id: str,
    target_kind: str,
    target_id: str,
    created_tick: int,
    scheduled_start_tick: int,
    scheduled_end_tick: int | None = None,
    required_inputs: List[str] | None = None,
    expected_outputs: List[str] | None = None,
    linked_project_id: str | None = None,
    linked_manifest_id: str | None = None,
    linked_event_ids: List[str] | None = None,
    status: str = "planned",
    extensions: Mapping[str, object] | None = None,
    commitment_id: str = "",
) -> dict:
    identity = {
        "commitment_type_id": str(commitment_type_id).strip(),
        "target_kind": str(target_kind).strip(),
        "target_id": str(target_id).strip(),
        "created_tick": int(max(0, int(created_tick))),
        "scheduled_start_tick": int(max(0, int(scheduled_start_tick))),
        "scheduled_end_tick": (
            None if scheduled_end_tick is None else int(max(0, int(scheduled_end_tick)))
        ),
    }
    if not commitment_id:
        commitment_id = "commitment.{}".format(canonical_sha256(identity)[:24])
    return normalize_commitment_row(
        {
            "schema_version": "1.0.0",
            "commitment_id": str(commitment_id),
            "commitment_type_id": str(commitment_type_id),
            "actor_subject_id": str(actor_subject_id).strip() or "subject.system",
            "target_kind": str(target_kind),
            "target_id": str(target_id),
            "created_tick": int(max(0, int(created_tick))),
            "scheduled_start_tick": int(max(0, int(scheduled_start_tick))),
            "scheduled_end_tick": (
                None if scheduled_end_tick is None else int(max(0, int(scheduled_end_tick)))
            ),
            "required_inputs": list(required_inputs or []),
            "expected_outputs": list(expected_outputs or []),
            "status": str(status or "planned"),
            "linked_project_id": linked_project_id,
            "linked_manifest_id": linked_manifest_id,
            "linked_event_ids": list(linked_event_ids or []),
            "extensions": dict(extensions or {}),
        }
    )


def _build_timeline(
    *,
    fidelity: str,
    event_ids: List[str],
    event_rows: List[dict],
    commitment_rows: List[dict],
) -> dict:
    if fidelity == "macro":
        type_counts: Dict[str, int] = {}
        for row in event_rows:
            event_type_id = str(row.get("event_type_id", "")).strip() or str(row.get("event_type", "")).strip() or "event.unknown"
            type_counts[event_type_id] = int(type_counts.get(event_type_id, 0) + 1)
        return {
            "fidelity": "macro",
            "event_count": int(len(event_ids)),
            "event_type_counts": dict((key, type_counts[key]) for key in sorted(type_counts.keys())),
        }
    timeline_rows = []
    commitment_by_id = dict(
        (str(row.get("commitment_id", "")).strip(), dict(row))
        for row in commitment_rows
        if isinstance(row, dict) and str(row.get("commitment_id", "")).strip()
    )
    for row in event_rows:
        event_id = str(row.get("event_id", "")).strip()
        ext = dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {}
        linked_commitment_id = str(ext.get("commitment_id", "")).strip() or str(row.get("commitment_id", "")).strip()
        timeline_rows.append(
            {
                "tick": max(0, _as_int(row.get("tick", 0), 0)),
                "event_id": event_id,
                "event_type_id": str(row.get("event_type_id", "")).strip() or str(row.get("event_type", "")).strip(),
                "linked_commitment_id": linked_commitment_id,
                "commitment_status": str((commitment_by_id.get(linked_commitment_id) or {}).get("status", "")).strip(),
            }
        )
    timeline_rows = sorted(timeline_rows, key=lambda item: (int(item.get("tick", 0)), str(item.get("event_id", ""))))
    if fidelity == "micro":
        return {
            "fidelity": "micro",
            "timeline": timeline_rows,
            "micro_seed_refs": [
                "seed.reenact.{}".format(canonical_sha256({"event_id": str(row.get("event_id", "")), "index": idx})[:16])
                for idx, row in enumerate(timeline_rows)
            ],
        }
    return {
        "fidelity": "meso",
        "timeline": timeline_rows,
    }


def build_reenactment_artifact(
    *,
    request_row: Mapping[str, object],
    event_stream_row: Mapping[str, object],
    commitment_rows: List[dict],
    batch_lineage_rows: List[dict] | None,
    max_cost_units: int,
    allow_micro_detail: bool,
) -> Tuple[dict, dict]:
    req = dict(request_row or {})
    stream = dict(event_stream_row or {})
    event_ids = _sorted_unique_strings(stream.get("event_ids"))
    event_rows = [dict(row) for row in list(stream.get("event_rows") or []) if isinstance(row, dict)]
    desired_fidelity = str(req.get("desired_fidelity", "macro")).strip() or "macro"
    if desired_fidelity not in ("macro", "meso", "micro"):
        desired_fidelity = "macro"
    if desired_fidelity == "micro" and not bool(allow_micro_detail):
        raise CommitmentError(
            REFUSAL_REENACTMENT_FORBIDDEN_BY_LAW,
            "micro reenactment detail is forbidden by law profile",
            {
                "request_id": str(req.get("request_id", "")),
                "target_id": str(req.get("target_id", "")),
            },
        )

    commitment_count = len([row for row in list(commitment_rows or []) if isinstance(row, dict)])
    event_count = len(event_ids)
    batch_count = len([row for row in list(batch_lineage_rows or []) if isinstance(row, dict)])

    macro_cost = max(1, event_count)
    meso_cost = max(macro_cost, event_count * 2 + commitment_count)
    micro_cost = max(meso_cost, event_count * 5 + commitment_count * 2 + batch_count)

    desired_max_cost = max(0, _as_int(max_cost_units, 0))
    fidelity_achieved = desired_fidelity
    if desired_fidelity == "micro" and micro_cost > desired_max_cost:
        fidelity_achieved = "meso"
    if fidelity_achieved == "meso" and meso_cost > desired_max_cost:
        fidelity_achieved = "macro"
    if macro_cost > desired_max_cost:
        raise CommitmentError(
            REFUSAL_REENACTMENT_BUDGET_EXCEEDED,
            "reenactment budget cannot satisfy macro fidelity",
            {
                "request_id": str(req.get("request_id", "")),
                "max_cost_units": int(desired_max_cost),
                "required_macro_cost": int(macro_cost),
            },
        )

    timeline_payload = _build_timeline(
        fidelity=fidelity_achieved,
        event_ids=event_ids,
        event_rows=event_rows,
        commitment_rows=[dict(row) for row in commitment_rows if isinstance(row, dict)],
    )
    inputs_hash = canonical_sha256(
        {
            "request": {
                "request_id": str(req.get("request_id", "")),
                "target_id": str(req.get("target_id", "")),
                "tick_range": dict(req.get("tick_range") or {}),
                "desired_fidelity": desired_fidelity,
            },
            "stream_hash": str(stream.get("stream_hash", "")),
            "commitment_ids": sorted(
                set(
                    str(row.get("commitment_id", "")).strip()
                    for row in commitment_rows
                    if isinstance(row, dict) and str(row.get("commitment_id", "")).strip()
                )
            ),
            "batch_lineage_ids": sorted(
                set(
                    str(row.get("batch_id", "")).strip()
                    for row in list(batch_lineage_rows or [])
                    if isinstance(row, dict) and str(row.get("batch_id", "")).strip()
                )
            ),
            "max_cost_units": int(desired_max_cost),
        }
    )
    reenactment_id = "reenactment.{}".format(canonical_sha256({"request_id": str(req.get("request_id", "")), "inputs_hash": inputs_hash})[:24])
    timeline_payload = dict(timeline_payload)
    timeline_payload["reenactment_id"] = reenactment_id
    timeline_payload["inputs_hash"] = inputs_hash
    timeline_payload["tick_range"] = dict(req.get("tick_range") or {})
    timeline_payload["target_id"] = str(req.get("target_id", "")).strip()
    timeline_payload["seed"] = canonical_sha256(
        {
            "target_id": str(req.get("target_id", "")).strip(),
            "tick_range": dict(req.get("tick_range") or {}),
            "inputs_hash": inputs_hash,
            "fidelity_achieved": fidelity_achieved,
        }
    )

    artifact_row = {
        "schema_version": "1.0.0",
        "reenactment_id": reenactment_id,
        "request_id": str(req.get("request_id", "")).strip(),
        "inputs_hash": inputs_hash,
        "output_timeline_ref": "",
        "fidelity_achieved": fidelity_achieved,
        "deterministic_fingerprint": "",
        "extensions": {
            "budget": {
                "max_cost_units": int(desired_max_cost),
                "macro_cost": int(macro_cost),
                "meso_cost": int(meso_cost),
                "micro_cost": int(micro_cost),
            },
            "derived_only": True,
            "degraded": fidelity_achieved != desired_fidelity,
        },
    }
    artifact_row["deterministic_fingerprint"] = _row_fingerprint(artifact_row)
    return artifact_row, timeline_payload
