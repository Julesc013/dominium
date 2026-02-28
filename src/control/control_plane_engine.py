"""Deterministic CTRL-1 control plane intent negotiation and resolution."""

from __future__ import annotations

import fnmatch
import os
from typing import Dict, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


CONTROL_REFUSAL_FORBIDDEN_BY_LAW = "refusal.ctrl.forbidden_by_law"
CONTROL_REFUSAL_ENTITLEMENT_MISSING = "refusal.ctrl.entitlement_missing"
CONTROL_REFUSAL_VIEW_FORBIDDEN = "refusal.ctrl.view_forbidden"
CONTROL_REFUSAL_FIDELITY_DENIED = "refusal.ctrl.fidelity_denied"
CONTROL_REFUSAL_DEGRADED = "refusal.ctrl.degraded"
CONTROL_REFUSAL_PLANNING_ONLY = "refusal.ctrl.planning_only"
CONTROL_REFUSAL_META_FORBIDDEN = "refusal.ctrl.meta_forbidden"
CONTROL_REFUSAL_REPLAY_MUTATION_FORBIDDEN = "refusal.ctrl.replay_mutation_forbidden"

DOWNGRADE_BUDGET = "downgrade.budget_insufficient"
DOWNGRADE_RANK_FAIRNESS = "downgrade.rank_fairness"
DOWNGRADE_EPISTEMIC = "downgrade.epistemic_limits"
DOWNGRADE_POLICY = "downgrade.policy_disallows"
DOWNGRADE_TARGET_NOT_AVAILABLE = "downgrade.target_not_available"

_ABSTRACTION_LEVELS = ("AL0", "AL1", "AL2", "AL3", "AL4")
_FIDELITY_LEVELS = ("macro", "meso", "micro")
_AL_RANK = dict((token, idx) for idx, token in enumerate(_ABSTRACTION_LEVELS))
_FIDELITY_RANK = dict((token, idx) for idx, token in enumerate(_FIDELITY_LEVELS))

DEFAULT_POLICY_ID = "ctrl.policy.player.diegetic"
DEFAULT_VIEW_POLICY_ID = "view.mode.first_person"
DEFAULT_ABSTRACTION_LEVEL = "AL0"
DEFAULT_FIDELITY = "meso"


def _to_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _canon_params(payload: object):
    if isinstance(payload, dict):
        return dict((str(key), _canon_params(payload[key])) for key in sorted(payload.keys()))
    if isinstance(payload, list):
        return [_canon_params(item) for item in payload]
    if payload is None:
        return None
    if isinstance(payload, (str, int, float, bool)):
        return payload
    return str(payload)


def _hash64(token: str, fallback_seed: object) -> str:
    value = str(token or "").strip()
    if len(value) == 64 and all(ch in "0123456789abcdefABCDEF" for ch in value):
        return value.lower()
    return canonical_sha256(fallback_seed)


def _refusal(
    reason_code: str,
    message: str,
    remediation_hint: str,
    relevant_ids: Mapping[str, object] | None = None,
    path: str = "$",
) -> dict:
    ids = {}
    for key, value in sorted((dict(relevant_ids or {})).items(), key=lambda row: str(row[0])):
        token = str(value).strip()
        if token:
            ids[str(key)] = token
    return {
        "reason_code": str(reason_code),
        "message": str(message),
        "remediation_hint": str(remediation_hint),
        "relevant_ids": ids,
        "path": str(path),
    }


def _registry_rows(payload: Mapping[str, object] | None, list_key: str) -> List[dict]:
    root = dict(payload or {})
    rows = root.get(list_key)
    if not isinstance(rows, list):
        rows = (dict(root.get("record") or {})).get(list_key)
    if not isinstance(rows, list):
        return []
    return [dict(row) for row in rows if isinstance(row, dict)]


def control_action_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    rows = _registry_rows(registry_payload, "actions")
    for row in sorted(rows, key=lambda item: str(item.get("action_id", ""))):
        action_id = str(row.get("action_id", "")).strip()
        if not action_id:
            continue
        display_name = str(row.get("display_name", "")).strip() or str(row.get("description", "")).strip() or action_id
        raw_produces = row.get("produces")
        if isinstance(raw_produces, dict):
            produces = {
                "process_id": str(raw_produces.get("process_id", "")).strip(),
                "task_type_id": str(raw_produces.get("task_type_id", "")).strip(),
                "plan_intent_type": str(raw_produces.get("plan_intent_type", "")).strip(),
            }
        else:
            legacy_process_id = str(row.get("process_id", "")).strip()
            if not legacy_process_id:
                legacy_process_id = str((dict(row.get("extensions") or {})).get("process_id", "")).strip()
            produces = {
                "process_id": legacy_process_id,
                "task_type_id": "",
                "plan_intent_type": "",
            }
        target_kinds = _sorted_unique_strings(row.get("target_kinds"))
        if not target_kinds:
            target_kinds = _sorted_unique_strings((dict(row.get("extensions") or {})).get("target_kinds"))
        out[action_id] = {
            "schema_version": "1.0.0",
            "action_id": action_id,
            "display_name": display_name,
            "produces": produces,
            "required_entitlements": _sorted_unique_strings(row.get("required_entitlements")),
            "required_capabilities": _sorted_unique_strings(row.get("required_capabilities")),
            "target_kinds": target_kinds,
            "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
        }
    return out


def control_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    rows = _registry_rows(registry_payload, "policies")
    for row in sorted(rows, key=lambda item: str(item.get("control_policy_id", ""))):
        policy_id = str(row.get("control_policy_id", "")).strip()
        if not policy_id:
            continue
        out[policy_id] = {
            "schema_version": "1.0.0",
            "control_policy_id": policy_id,
            "description": str(row.get("description", "")).strip(),
            "allowed_actions": _sorted_unique_strings(row.get("allowed_actions")),
            "allowed_abstraction_levels": _sorted_unique_strings(row.get("allowed_abstraction_levels")),
            "allowed_view_policies": _sorted_unique_strings(row.get("allowed_view_policies")),
            "allowed_fidelity_ranges": _sorted_unique_strings(row.get("allowed_fidelity_ranges")),
            "downgrade_rules": dict(row.get("downgrade_rules") or {}) if isinstance(row.get("downgrade_rules"), dict) else {},
            "strictness": str(row.get("strictness", "")).strip() or "C0",
            "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
        }
    return out


def _al_requested(value: object) -> str:
    token = str(value or "").strip()
    if token in _AL_RANK:
        return token
    return DEFAULT_ABSTRACTION_LEVEL


def _fidelity_requested(value: object) -> str:
    token = str(value or "").strip()
    if token in _FIDELITY_RANK:
        return token
    return DEFAULT_FIDELITY


def _is_ranked_server(policy_context: Mapping[str, object] | None) -> bool:
    payload = dict(policy_context or {})
    if bool(payload.get("ranked_server", False)):
        return True
    server_profile_id = str(payload.get("server_profile_id", "")).strip().lower()
    return "rank" in server_profile_id


def _path_allowed(action_id: str, patterns: List[str]) -> bool:
    token = str(action_id).strip()
    for pattern in list(patterns or []):
        if fnmatch.fnmatch(token, str(pattern)):
            return True
    return False


def _resolve_policy_id(control_intent: Mapping[str, object], policy_context: Mapping[str, object] | None) -> str:
    intent_ext = dict((dict(control_intent or {})).get("extensions") or {})
    for token in (
        intent_ext.get("control_policy_id"),
        (dict(policy_context or {})).get("control_policy_id"),
    ):
        policy_id = str(token or "").strip()
        if policy_id:
            return policy_id
    requested = _al_requested(((dict(control_intent or {})).get("request_vector") or {}).get("abstraction_level_requested"))
    if requested == "AL4":
        return "ctrl.policy.admin.meta"
    if requested == "AL3":
        return "ctrl.policy.planner"
    if requested == "AL2":
        return "ctrl.policy.scheduler"
    return DEFAULT_POLICY_ID


def build_control_intent(
    *,
    requester_subject_id: str,
    requested_action_id: str,
    target_kind: str = "none",
    target_id: str | None = None,
    parameters: Mapping[str, object] | None = None,
    abstraction_level_requested: str = DEFAULT_ABSTRACTION_LEVEL,
    fidelity_requested: str = DEFAULT_FIDELITY,
    view_requested: str = DEFAULT_VIEW_POLICY_ID,
    inspection_requested: str = "none",
    reenactment_requested: str = "none",
    created_tick: int = 0,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "control_intent_id": "",
        "requester_subject_id": str(requester_subject_id).strip() or "subject.unknown",
        "target_kind": str(target_kind).strip() or "none",
        "target_id": None if target_id is None else (str(target_id).strip() or None),
        "requested_action_id": str(requested_action_id).strip(),
        "parameters": _canon_params(dict(parameters or {})),
        "request_vector": {
            "abstraction_level_requested": _al_requested(abstraction_level_requested),
            "fidelity_requested": _fidelity_requested(fidelity_requested),
            "view_requested": str(view_requested).strip() or DEFAULT_VIEW_POLICY_ID,
            "inspection_requested": str(inspection_requested).strip() or "none",
            "reenactment_requested": str(reenactment_requested).strip() or "none",
        },
        "created_tick": int(max(0, _to_int(created_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    payload["control_intent_id"] = "control.intent.{}".format(canonical_sha256(payload)[:24])
    seed = dict(payload)
    seed["deterministic_fingerprint"] = ""
    payload["deterministic_fingerprint"] = canonical_sha256(seed)
    return payload


def _resolve_abstraction_level(requested: str, allowed: List[str]) -> Tuple[str, List[str]]:
    req = _al_requested(requested)
    rows = [token for token in list(allowed or []) if token in _AL_RANK]
    if not rows:
        return req, []
    if req in rows:
        return req, []
    req_rank = _AL_RANK[req]
    candidates = sorted(rows, key=lambda token: _AL_RANK[token], reverse=True)
    for token in candidates:
        if _AL_RANK[token] <= req_rank:
            return token, [DOWNGRADE_POLICY]
    return sorted(rows, key=lambda token: _AL_RANK[token])[0], [DOWNGRADE_POLICY]


def _resolve_fidelity(
    requested: str,
    allowed: List[str],
    policy_context: Mapping[str, object] | None,
) -> Tuple[str, List[str]]:
    req = _fidelity_requested(requested)
    rows = [token for token in list(allowed or []) if token in _FIDELITY_RANK]
    if not rows:
        rows = list(_FIDELITY_LEVELS)
    reasons: List[str] = []
    max_fidelity = str((dict(policy_context or {})).get("max_control_fidelity", "")).strip()
    if max_fidelity in _FIDELITY_RANK and _FIDELITY_RANK[req] > _FIDELITY_RANK[max_fidelity]:
        req = max_fidelity
        reasons.append(DOWNGRADE_BUDGET)
    if req in rows:
        return req, reasons
    req_rank = _FIDELITY_RANK[req]
    candidates = sorted(rows, key=lambda token: _FIDELITY_RANK[token], reverse=True)
    for token in candidates:
        if _FIDELITY_RANK[token] <= req_rank:
            reasons.append(DOWNGRADE_POLICY)
            return token, reasons
    reasons.append(DOWNGRADE_POLICY)
    return sorted(rows, key=lambda token: _FIDELITY_RANK[token])[0], reasons


def _resolve_view(requested: str, allowed: List[str]) -> Tuple[str, List[str]]:
    req = str(requested or "").strip() or DEFAULT_VIEW_POLICY_ID
    rows = _sorted_unique_strings(allowed)
    if not rows:
        return req, []
    if req in rows:
        return req, []
    return rows[0], [DOWNGRADE_POLICY]


def _build_resolution_id(seed: Mapping[str, object]) -> str:
    return "control.resolution.{}".format(canonical_sha256(seed)[:24])


def _resolve_process_inputs(params: Mapping[str, object], process_id: str) -> dict:
    payload = dict(params or {})
    nested = payload.get("inputs")
    if isinstance(nested, dict):
        out = dict(nested)
    else:
        out = dict(payload)
    process_token = str(process_id).strip()
    param_process = str(out.get("process_id", "")).strip()
    if param_process and ((not process_token) or (param_process == process_token)):
        out.pop("process_id", None)
    return _canon_params(out) if isinstance(out, dict) else {}


def _intent_row(
    *,
    control_intent: Mapping[str, object],
    process_id: str,
    inputs: Mapping[str, object],
) -> dict:
    intent_seed = {
        "control_intent_id": str((dict(control_intent or {})).get("control_intent_id", "")),
        "process_id": str(process_id),
        "inputs": _canon_params(dict(inputs or {})),
    }
    intent_id = "intent.control.{}".format(canonical_sha256(intent_seed)[:16])
    authority_context_ref = dict((dict(control_intent or {})).get("extensions") or {}).get("authority_context_ref")
    if not isinstance(authority_context_ref, dict):
        authority_context_ref = {}
    return {
        "intent_id": intent_id,
        "process_id": str(process_id),
        "inputs": _canon_params(dict(inputs or {})),
        "authority_context_ref": {
            "authority_origin": str(authority_context_ref.get("authority_origin", "client")),
            "law_profile_id": str(authority_context_ref.get("law_profile_id", "")),
        },
        "extensions": {
            "control_intent_id": str((dict(control_intent or {})).get("control_intent_id", "")),
        },
    }


def _build_envelope(
    *,
    intent: Mapping[str, object],
    control_intent: Mapping[str, object],
    policy_context: Mapping[str, object] | None,
) -> dict:
    payload = dict(policy_context or {})
    submission_tick = int(
        max(0, _to_int(payload.get("submission_tick", (dict(control_intent or {})).get("created_tick", 0)), 0))
    )
    sequence = int(max(0, _to_int(payload.get("deterministic_sequence_number", 0), 0)))
    source_peer_id = (
        str(payload.get("peer_id", "")).strip()
        or str((dict(control_intent or {})).get("requester_subject_id", "")).strip()
        or "peer.local"
    )
    source_shard = str(payload.get("source_shard_id", "shard.0")).strip() or "shard.0"
    target_shard = str(payload.get("target_shard_id", source_shard)).strip() or source_shard
    authority_context_ref = dict((dict(intent or {})).get("authority_context_ref") or {})
    return {
        "schema_version": "1.0.0",
        "envelope_id": "env.{}.tick.{}.seq.{}".format(source_peer_id, submission_tick, str(sequence).zfill(4)),
        "authority_summary": {
            "authority_origin": str(authority_context_ref.get("authority_origin", "client")),
            "law_profile_id": str(authority_context_ref.get("law_profile_id", "")),
        },
        "source_peer_id": source_peer_id,
        "source_shard_id": source_shard,
        "target_shard_id": target_shard,
        "submission_tick": int(submission_tick),
        "deterministic_sequence_number": int(sequence),
        "intent_id": str((dict(intent or {})).get("intent_id", "")),
        "payload_schema_id": "dominium.intent.process.v1",
        "payload": {
            "process_id": str((dict(intent or {})).get("process_id", "")),
            "inputs": _canon_params(dict((dict(intent or {})).get("inputs") or {})),
        },
        "pack_lock_hash": _hash64(str(payload.get("pack_lock_hash", "")), {"source_peer_id": source_peer_id}),
        "registry_hashes": dict(payload.get("registry_hashes") or {}),
        "signature": "",
        "extensions": {
            "control_plane_dispatch": True,
            "control_intent_id": str((dict(control_intent or {})).get("control_intent_id", "")),
        },
    }


def _decision_log_extensions(policy_context: Mapping[str, object] | None) -> dict:
    payload = dict(policy_context or {})
    ir_context = dict(payload.get("control_ir_execution") or {})
    if not ir_context:
        return {}
    normalized = {}
    for key in sorted(ir_context.keys()):
        token = str(key).strip()
        if not token:
            continue
        value = ir_context.get(key)
        if isinstance(value, (str, int, float, bool)) or value is None:
            if isinstance(value, str):
                stripped = str(value).strip()
                if not stripped:
                    continue
                normalized[token] = stripped
            elif value is not None:
                normalized[token] = value
            continue
        normalized[token] = _canon_params(value)
    if not normalized:
        return {}
    return {"control_ir_execution": normalized}


def _decision_log_row(
    *,
    control_intent: Mapping[str, object],
    control_policy_id: str,
    resolved_vector: Mapping[str, object],
    refusal: Mapping[str, object] | None,
    downgrade_reasons: List[str],
    emitted_envelopes: List[Mapping[str, object]],
    decision_extensions: Mapping[str, object] | None = None,
) -> dict:
    tick = int(max(0, _to_int((dict(control_intent or {})).get("created_tick", 0), 0)))
    emitted_ids = sorted(
        set(
            str((dict(row or {})).get("intent_id", "")).strip()
            or str((dict(row or {})).get("envelope_id", "")).strip()
            for row in list(emitted_envelopes or [])
            if isinstance(row, Mapping)
        )
    )
    seed = {
        "tick": int(tick),
        "requester_subject_id": str((dict(control_intent or {})).get("requester_subject_id", "")),
        "control_intent_id": str((dict(control_intent or {})).get("control_intent_id", "")),
        "control_policy_id": str(control_policy_id),
        "resolved_vector": dict(resolved_vector or {}),
        "reasons": dict(refusal or {}),
        "downgrade_reasons": list(downgrade_reasons or []),
        "emitted_ids": list(emitted_ids),
    }
    log_id = "control.log.{}".format(canonical_sha256(seed)[:24])
    row = {
        "schema_version": "0.1.0",
        "log_id": log_id,
        "tick": int(tick),
        "requester_subject_id": str((dict(control_intent or {})).get("requester_subject_id", "")),
        "control_intent_id": str((dict(control_intent or {})).get("control_intent_id", "")),
        "control_policy_id": str(control_policy_id),
        "resolved_vector": dict(resolved_vector or {}),
        "reasons": {
            "refusal": dict(refusal or {}),
            "downgrade_reasons": sorted(
                set(str(item).strip() for item in list(downgrade_reasons or []) if str(item).strip())
            ),
        },
        "emitted_ids": list(emitted_ids),
        "deterministic_fingerprint": "",
        "extensions": dict(decision_extensions or {}),
    }
    row_seed = dict(row)
    row_seed["deterministic_fingerprint"] = ""
    row["deterministic_fingerprint"] = canonical_sha256(row_seed)
    return row


def _write_decision_log(repo_root: str, log_row: Mapping[str, object]) -> str:
    repo = str(repo_root or "").strip()
    if not repo:
        return str((dict(log_row or {})).get("log_id", ""))
    rel = os.path.join("run_meta", "control_decisions", "{}.json".format(str((dict(log_row or {})).get("log_id", ""))))
    abs_path = os.path.join(repo, rel)
    parent = os.path.dirname(abs_path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(log_row or {})))
        handle.write("\n")
    return rel.replace("\\", "/")


def _build_refused_resolution(
    *,
    control_intent_id: str,
    control_policy_id: str,
    resolved_vector: Mapping[str, object],
    refusal_payload: Mapping[str, object],
    downgrade_reasons: List[str],
    log_ref: str,
) -> dict:
    resolution = {
        "schema_version": "1.0.0",
        "resolution_id": _build_resolution_id({"control_intent_id": control_intent_id, "refusal": dict(refusal_payload or {})}),
        "input_control_intent_id": str(control_intent_id),
        "allowed": False,
        "resolved_vector": dict(resolved_vector or {}),
        "emitted_intents": [],
        "emitted_intent_envelopes": [],
        "emitted_commitment_ids": [],
        "refusal": dict(refusal_payload or {}),
        "downgrade_reasons": sorted(set(str(item).strip() for item in list(downgrade_reasons or []) if str(item).strip())),
        "decision_log_ref": str(log_ref),
        "deterministic_fingerprint": "",
        "extensions": {"control_policy_id": str(control_policy_id)},
    }
    seed = dict(resolution)
    seed["deterministic_fingerprint"] = ""
    resolution["deterministic_fingerprint"] = canonical_sha256(seed)
    return resolution


def build_control_resolution(
    *,
    control_intent: Mapping[str, object],
    law_profile: Mapping[str, object] | None,
    authority_context: Mapping[str, object] | None,
    policy_context: Mapping[str, object] | None = None,
    control_action_registry: Mapping[str, object] | None = None,
    control_policy_registry: Mapping[str, object] | None = None,
    repo_root: str = "",
) -> dict:
    intent = dict(control_intent or {})
    request_vector = dict(intent.get("request_vector") or {})
    params = dict(intent.get("parameters") or {})
    authority = dict(authority_context or {})
    law = dict(law_profile or {})
    policy_context_payload = dict(policy_context or {})
    decision_log_extensions = _decision_log_extensions(policy_context_payload)

    control_intent_id = str(intent.get("control_intent_id", "")).strip()
    if not control_intent_id:
        refusal_payload = _refusal(
            CONTROL_REFUSAL_FORBIDDEN_BY_LAW,
            "control_intent_id is required",
            "Build intent with build_control_intent before resolution.",
            {},
            "$.control_intent_id",
        )
        return {"result": "refused", "refusal": refusal_payload}

    action_id = str(intent.get("requested_action_id", "")).strip()
    if not action_id:
        refusal_payload = _refusal(
            CONTROL_REFUSAL_FORBIDDEN_BY_LAW,
            "requested_action_id is required",
            "Provide requested_action_id referencing control_action registry.",
            {},
            "$.requested_action_id",
        )
        return {"result": "refused", "refusal": refusal_payload}

    action_rows = control_action_rows_by_id(control_action_registry)
    action_row = dict(action_rows.get(action_id) or {})
    if not action_row:
        fallback_process_id = str(params.get("process_id", "")).strip()
        if not fallback_process_id:
            refusal_payload = _refusal(
                CONTROL_REFUSAL_FORBIDDEN_BY_LAW,
                "requested action is unknown",
                "Register action in control_action_registry or pass process_id adapter field.",
                {"requested_action_id": action_id},
                "$.requested_action_id",
            )
            return {"result": "refused", "refusal": refusal_payload}
        action_row = {
            "action_id": action_id,
            "display_name": action_id,
            "required_entitlements": [],
            "required_capabilities": [],
            "target_kinds": [],
            "produces": {
                "process_id": fallback_process_id,
                "task_type_id": "",
                "plan_intent_type": "",
            },
            "extensions": {"adapter": "legacy.process_id"},
        }

    policy_rows = control_policy_rows_by_id(control_policy_registry)
    control_policy_id = _resolve_policy_id(intent, policy_context_payload)
    policy_row = dict(policy_rows.get(control_policy_id) or {})
    if not policy_row:
        policy_row = {
            "control_policy_id": control_policy_id,
            "allowed_actions": ["*"],
            "allowed_abstraction_levels": list(_ABSTRACTION_LEVELS),
            "allowed_view_policies": [DEFAULT_VIEW_POLICY_ID],
            "allowed_fidelity_ranges": list(_FIDELITY_LEVELS),
            "strictness": "C0",
            "extensions": {},
        }

    requested_al = _al_requested(request_vector.get("abstraction_level_requested"))
    requested_fidelity = _fidelity_requested(request_vector.get("fidelity_requested"))
    requested_view = str(request_vector.get("view_requested", "")).strip() or DEFAULT_VIEW_POLICY_ID

    resolved_al, al_reasons = _resolve_abstraction_level(
        requested=requested_al,
        allowed=_sorted_unique_strings(policy_row.get("allowed_abstraction_levels")),
    )
    resolved_fidelity, fidelity_reasons = _resolve_fidelity(
        requested=requested_fidelity,
        allowed=_sorted_unique_strings(policy_row.get("allowed_fidelity_ranges")),
        policy_context=policy_context_payload,
    )
    resolved_view, view_reasons = _resolve_view(
        requested=requested_view,
        allowed=_sorted_unique_strings(policy_row.get("allowed_view_policies")),
    )
    resolved_vector = {
        "abstraction_level_resolved": resolved_al,
        "fidelity_resolved": resolved_fidelity,
        "view_resolved": resolved_view,
    }
    downgrade_reasons = sorted(set(al_reasons + fidelity_reasons + view_reasons))

    allowed_action_patterns = _sorted_unique_strings(policy_row.get("allowed_actions"))
    if allowed_action_patterns and (not _path_allowed(action_id, allowed_action_patterns)):
        refusal_payload = _refusal(
            CONTROL_REFUSAL_FORBIDDEN_BY_LAW,
            "action is not allowed by control policy",
            "Use an action listed in control policy or switch policy under lawful authority.",
            {"requested_action_id": action_id, "control_policy_id": control_policy_id},
            "$.requested_action_id",
        )
        log_row = _decision_log_row(
            control_intent=intent,
            control_policy_id=control_policy_id,
            resolved_vector=resolved_vector,
            refusal=refusal_payload,
            downgrade_reasons=downgrade_reasons,
            emitted_envelopes=[],
            decision_extensions=decision_log_extensions,
        )
        log_ref = _write_decision_log(repo_root, log_row)
        return {
            "result": "refused",
            "resolution": _build_refused_resolution(
                control_intent_id=control_intent_id,
                control_policy_id=control_policy_id,
                resolved_vector=resolved_vector,
                refusal_payload=refusal_payload,
                downgrade_reasons=downgrade_reasons,
                log_ref=log_ref,
            ),
            "refusal": refusal_payload,
        }

    authority_entitlements = set(_sorted_unique_strings(authority.get("entitlements")))
    missing_entitlements = [
        token for token in _sorted_unique_strings(action_row.get("required_entitlements")) if token not in authority_entitlements
    ]
    if missing_entitlements:
        refusal_payload = _refusal(
            CONTROL_REFUSAL_ENTITLEMENT_MISSING,
            "action requires missing entitlements",
            "Grant missing entitlements or choose an action allowed by current authority.",
            {"missing_entitlements": ",".join(missing_entitlements), "requested_action_id": action_id},
            "$.authority_context.entitlements",
        )
        log_row = _decision_log_row(
            control_intent=intent,
            control_policy_id=control_policy_id,
            resolved_vector=resolved_vector,
            refusal=refusal_payload,
            downgrade_reasons=downgrade_reasons,
            emitted_envelopes=[],
            decision_extensions=decision_log_extensions,
        )
        log_ref = _write_decision_log(repo_root, log_row)
        return {
            "result": "refused",
            "resolution": _build_refused_resolution(
                control_intent_id=control_intent_id,
                control_policy_id=control_policy_id,
                resolved_vector=resolved_vector,
                refusal_payload=refusal_payload,
                downgrade_reasons=downgrade_reasons,
                log_ref=log_ref,
            ),
            "refusal": refusal_payload,
        }

    if _is_ranked_server(policy_context_payload) and requested_al == "AL4":
        refusal_payload = _refusal(
            CONTROL_REFUSAL_META_FORBIDDEN,
            "ranked server forbids AL4 meta control intents",
            "Use AL0-AL3 actions on ranked servers.",
            {"requested_action_id": action_id, "abstraction_level_requested": requested_al},
            "$.request_vector.abstraction_level_requested",
        )
        log_row = _decision_log_row(
            control_intent=intent,
            control_policy_id=control_policy_id,
            resolved_vector=resolved_vector,
            refusal=refusal_payload,
            downgrade_reasons=sorted(set(downgrade_reasons + [DOWNGRADE_RANK_FAIRNESS])),
            emitted_envelopes=[],
            decision_extensions=decision_log_extensions,
        )
        log_ref = _write_decision_log(repo_root, log_row)
        return {
            "result": "refused",
            "resolution": _build_refused_resolution(
                control_intent_id=control_intent_id,
                control_policy_id=control_policy_id,
                resolved_vector=resolved_vector,
                refusal_payload=refusal_payload,
                downgrade_reasons=sorted(set(downgrade_reasons + [DOWNGRADE_RANK_FAIRNESS])),
                log_ref=log_ref,
            ),
            "refusal": refusal_payload,
        }

    produces = dict(action_row.get("produces") or {})
    process_id = str(produces.get("process_id", "")).strip() or str(params.get("process_id", "")).strip()
    task_type_id = str(produces.get("task_type_id", "")).strip()
    plan_intent_type = str(produces.get("plan_intent_type", "")).strip()

    emitted_intents: List[dict] = []
    if plan_intent_type and resolved_al in ("AL0", "AL1", "AL2"):
        refusal_payload = _refusal(
            CONTROL_REFUSAL_PLANNING_ONLY,
            "planning actions are derived-only at current abstraction",
            "Request AL3 planning abstraction or switch to executable action.",
            {"requested_action_id": action_id, "plan_intent_type": plan_intent_type},
            "$.requested_action_id",
        )
        log_row = _decision_log_row(
            control_intent=intent,
            control_policy_id=control_policy_id,
            resolved_vector=resolved_vector,
            refusal=refusal_payload,
            downgrade_reasons=downgrade_reasons,
            emitted_envelopes=[],
            decision_extensions=decision_log_extensions,
        )
        log_ref = _write_decision_log(repo_root, log_row)
        return {
            "result": "refused",
            "resolution": _build_refused_resolution(
                control_intent_id=control_intent_id,
                control_policy_id=control_policy_id,
                resolved_vector=resolved_vector,
                refusal_payload=refusal_payload,
                downgrade_reasons=downgrade_reasons,
                log_ref=log_ref,
            ),
            "refusal": refusal_payload,
        }

    if task_type_id:
        task_inputs = _resolve_process_inputs(params=params, process_id=process_id)
        task_inputs["task_type_id"] = task_type_id
        if "process_id_to_execute" not in task_inputs and process_id:
            task_inputs["process_id_to_execute"] = process_id
        emitted_intents.append(
            _intent_row(control_intent=intent, process_id="process.task_create", inputs=task_inputs)
        )
    elif process_id:
        process_inputs = _resolve_process_inputs(params=params, process_id=process_id)
        allowed_processes = set(_sorted_unique_strings(law.get("allowed_processes")))
        forbidden_processes = set(_sorted_unique_strings(law.get("forbidden_processes")))
        if process_id in forbidden_processes or (allowed_processes and process_id not in allowed_processes):
            refusal_payload = _refusal(
                CONTROL_REFUSAL_FORBIDDEN_BY_LAW,
                "action process is forbidden by law profile",
                "Use a process listed in law_profile.allowed_processes.",
                {"requested_action_id": action_id, "process_id": process_id},
                "$.requested_action_id",
            )
            log_row = _decision_log_row(
                control_intent=intent,
                control_policy_id=control_policy_id,
                resolved_vector=resolved_vector,
                refusal=refusal_payload,
                downgrade_reasons=downgrade_reasons,
                emitted_envelopes=[],
                decision_extensions=decision_log_extensions,
            )
            log_ref = _write_decision_log(repo_root, log_row)
            return {
                "result": "refused",
                "resolution": _build_refused_resolution(
                    control_intent_id=control_intent_id,
                    control_policy_id=control_policy_id,
                    resolved_vector=resolved_vector,
                    refusal_payload=refusal_payload,
                    downgrade_reasons=downgrade_reasons,
                    log_ref=log_ref,
                ),
                    "refusal": refusal_payload,
                }
        emitted_intents.append(_intent_row(control_intent=intent, process_id=process_id, inputs=process_inputs))

    emitted_envelopes = sorted(
        (_build_envelope(intent=row, control_intent=intent, policy_context=policy_context_payload) for row in emitted_intents),
        key=lambda row: (
            int(_to_int(row.get("submission_tick", 0), 0)),
            int(_to_int(row.get("deterministic_sequence_number", 0), 0)),
            str(row.get("envelope_id", "")),
        ),
    )
    log_row = _decision_log_row(
        control_intent=intent,
        control_policy_id=control_policy_id,
        resolved_vector=resolved_vector,
        refusal=None,
        downgrade_reasons=downgrade_reasons,
        emitted_envelopes=emitted_envelopes,
        decision_extensions=decision_log_extensions,
    )
    log_ref = _write_decision_log(repo_root, log_row)

    resolution = {
        "schema_version": "1.0.0",
        "resolution_id": _build_resolution_id(
            {
                "control_intent_id": control_intent_id,
                "resolved_vector": resolved_vector,
                "emitted_intent_ids": [str(row.get("intent_id", "")) for row in emitted_intents],
            }
        ),
        "input_control_intent_id": control_intent_id,
        "allowed": True,
        "resolved_vector": resolved_vector,
        "emitted_intents": emitted_intents,
        "emitted_intent_envelopes": emitted_envelopes,
        "emitted_commitment_ids": [],
        "refusal": None,
        "downgrade_reasons": downgrade_reasons,
        "decision_log_ref": str(log_ref),
        "deterministic_fingerprint": "",
        "extensions": {
            "control_policy_id": control_policy_id,
            "control_action_id": action_id,
            "strictness": str(policy_row.get("strictness", "C0")),
        },
    }
    seed = dict(resolution)
    seed["deterministic_fingerprint"] = ""
    resolution["deterministic_fingerprint"] = canonical_sha256(seed)
    return {"result": "complete", "resolution": resolution}


__all__ = [
    "CONTROL_REFUSAL_DEGRADED",
    "build_control_intent",
    "build_control_resolution",
    "control_action_rows_by_id",
    "control_policy_rows_by_id",
]
