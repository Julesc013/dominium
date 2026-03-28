"""Deterministic CTRL-1 control plane intent negotiation and resolution."""

from __future__ import annotations

import fnmatch
import os
from typing import Dict, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256

from .capability import capability_binding_rows, resolve_missing_capabilities
from .effects import REFUSAL_EFFECT_FORBIDDEN, get_effective_modifier_map
from .negotiation import negotiate_request


CONTROL_REFUSAL_FORBIDDEN_BY_LAW = "refusal.ctrl.forbidden_by_law"
CONTROL_REFUSAL_ENTITLEMENT_MISSING = "refusal.ctrl.entitlement_missing"
CONTROL_REFUSAL_VIEW_FORBIDDEN = "refusal.ctrl.view_forbidden"
CONTROL_REFUSAL_FIDELITY_DENIED = "refusal.ctrl.fidelity_denied"
CONTROL_REFUSAL_DEGRADED = "refusal.ctrl.degraded"
CONTROL_REFUSAL_PLANNING_ONLY = "refusal.ctrl.planning_only"
CONTROL_REFUSAL_META_FORBIDDEN = "refusal.ctrl.meta_forbidden"
CONTROL_REFUSAL_REPLAY_MUTATION_FORBIDDEN = "refusal.ctrl.replay_mutation_forbidden"
CONTROL_REFUSAL_SPEC_NONCOMPLIANT = "refusal.spec.noncompliant"

DOWNGRADE_BUDGET = "downgrade.budget_insufficient"
DOWNGRADE_RANK_FAIRNESS = "downgrade.rank_fairness"
DOWNGRADE_EPISTEMIC = "downgrade.epistemic_limits"
DOWNGRADE_POLICY = "downgrade.policy_disallows"
DOWNGRADE_TARGET_NOT_AVAILABLE = "downgrade.target_not_available"
DOWNGRADE_EFFECT_VISIBILITY = "downgrade.effect.visibility_reduction"
DOWNGRADE_SPEC_NONCOMPLIANT = "downgrade.spec.noncompliant"

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


def _coerce_string_list(values: object) -> List[str]:
    if isinstance(values, list):
        return _sorted_unique_strings(values)
    token = str(values or "").strip()
    if token:
        return [token]
    return []


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


def action_template_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    rows = _registry_rows(registry_payload, "templates")
    for row in sorted(rows, key=lambda item: str(item.get("action_template_id", ""))):
        action_template_id = str(row.get("action_template_id", "")).strip()
        if not action_template_id:
            continue
        action_family_id = str(row.get("action_family_id", "")).strip()
        if not action_family_id:
            continue
        out[action_template_id] = {
            "schema_version": "1.0.0",
            "action_template_id": action_template_id,
            "action_family_id": action_family_id,
            "required_tool_tags": _sorted_unique_strings(row.get("required_tool_tags")),
            "required_surface_types": _sorted_unique_strings(row.get("required_surface_types")),
            "required_capabilities": _sorted_unique_strings(row.get("required_capabilities")),
            "produced_artifact_types": _sorted_unique_strings(row.get("produced_artifact_types")),
            "produced_hazard_types": _sorted_unique_strings(row.get("produced_hazard_types")),
            "affected_substrates": _sorted_unique_strings(row.get("affected_substrates")),
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


def _replay_read_only_process_allowed(process_id: str) -> bool:
    token = str(process_id or "").strip()
    if not token:
        return True
    return token in {
        "process.camera_set_view_mode",
        "process.view_bind",
        "process.reenactment_generate",
        "process.reenactment_play",
        "process.reenactment_request",
        "process.fidelity_request",
    }


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


def _policy_dict(payload: Mapping[str, object] | None, key: str) -> dict:
    if not isinstance(payload, Mapping):
        return {}
    row = payload.get(key)
    if not isinstance(row, Mapping):
        return {}
    return dict(row)


def _policy_rows(payload: Mapping[str, object] | None, key: str) -> List[dict]:
    if not isinstance(payload, Mapping):
        return []
    rows = payload.get(key)
    if not isinstance(rows, list):
        return []
    return [dict(row) for row in rows if isinstance(row, Mapping)]


def _normalize_decision_extension_payload(payload: Mapping[str, object] | None) -> dict:
    out = {}
    for key in sorted((dict(payload or {})).keys()):
        token = str(key).strip()
        if not token:
            continue
        value = (dict(payload or {})).get(key)
        if isinstance(value, (str, int, float, bool)) or value is None:
            if isinstance(value, str):
                stripped = str(value).strip()
                if not stripped:
                    continue
                out[token] = stripped
            elif value is not None:
                out[token] = value
            continue
        out[token] = _canon_params(value)
    return out


def _effect_influence(
    *,
    control_intent: Mapping[str, object],
    policy_context: Mapping[str, object] | None,
    process_id: str,
) -> dict:
    payload = dict(policy_context or {})
    target_id = str((dict(control_intent or {})).get("target_id", "")).strip()
    if not target_id:
        return {}
    effect_rows = _policy_rows(payload, "effect_rows")
    if not effect_rows:
        return {}
    current_tick = int(
        max(
            0,
            _to_int(
                payload.get("submission_tick", (dict(control_intent or {})).get("created_tick", 0)),
                0,
            ),
        )
    )
    modifier_map = get_effective_modifier_map(
        target_id=target_id,
        keys=[
            "access_restricted",
            "visibility_permille",
            "max_speed_permille",
            "tool_efficiency_permille",
            "machine_output_permille",
            "pressure_hazard_warning",
        ],
        effect_rows=effect_rows,
        current_tick=current_tick,
        effect_type_registry=_policy_dict(payload, "effect_type_registry"),
        stacking_policy_registry=_policy_dict(payload, "stacking_policy_registry"),
    )
    modifiers = dict(modifier_map.get("modifiers") or {})
    filtered_modifiers = {}
    for key in sorted(modifiers.keys()):
        row = dict(modifiers.get(key) or {})
        if (not bool(row.get("present", False))) and int(_to_int(row.get("value", 0), 0)) == 0:
            continue
        filtered_modifiers[str(key)] = {
            "present": bool(row.get("present", False)),
            "value": int(_to_int(row.get("value", 0), 0)),
            "applied_effect_ids": _sorted_unique_strings(row.get("applied_effect_ids")),
            "stacking_modes": _sorted_unique_strings(row.get("stacking_modes")),
        }
    if not filtered_modifiers:
        return {}
    out = {
        "target_id": target_id,
        "process_id": str(process_id or "").strip(),
        "query_tick": int(current_tick),
        "query_cost_units": int(max(0, _to_int(modifier_map.get("query_cost_units", 0), 0))),
        "modifiers": dict((key, filtered_modifiers[key]) for key in sorted(filtered_modifiers.keys())),
        "deterministic_fingerprint": "",
    }
    seed = dict(out)
    seed["deterministic_fingerprint"] = ""
    out["deterministic_fingerprint"] = canonical_sha256(seed)
    return out


def _decision_log_extensions(policy_context: Mapping[str, object] | None) -> dict:
    payload = dict(policy_context or {})
    out = {}
    ir_context = _normalize_decision_extension_payload(payload.get("control_ir_execution"))
    if ir_context:
        out["control_ir_execution"] = dict(ir_context)
    effect_context = _normalize_decision_extension_payload(payload.get("effect_influence"))
    if effect_context:
        out["effect_influence"] = dict(effect_context)
    spec_context = _normalize_decision_extension_payload(payload.get("spec_compliance"))
    if spec_context:
        out["spec_compliance"] = dict(spec_context)
    return out


def _negotiation_downgrade_reasons(negotiation_result: Mapping[str, object]) -> List[str]:
    reasons: List[str] = []
    for row in list((dict(negotiation_result or {})).get("downgrade_entries") or []):
        if not isinstance(row, Mapping):
            continue
        reason_code = str(row.get("reason_code", "")).strip()
        if reason_code:
            reasons.append(reason_code)
    return sorted(set(reasons))


def _policy_ids_applied(
    negotiation_result: Mapping[str, object],
    control_policy_id: str,
) -> List[str]:
    payload = dict(negotiation_result or {})
    ext = dict(payload.get("extensions") or {})
    policy_ids = _sorted_unique_strings(ext.get("policy_ids_applied"))
    fallback = str(control_policy_id or "").strip()
    if fallback and fallback not in policy_ids:
        policy_ids.append(fallback)
    return sorted(set(policy_ids))


def _negotiation_with_refusal_code(
    negotiation_result: Mapping[str, object],
    reason_code: str,
) -> dict:
    payload = dict(negotiation_result or {})
    refusal_codes = _sorted_unique_strings(payload.get("refusal_codes"))
    token = str(reason_code or "").strip()
    if token and token not in refusal_codes:
        refusal_codes.append(token)
    payload["refusal_codes"] = sorted(set(refusal_codes))
    seed = dict(payload)
    seed["deterministic_fingerprint"] = ""
    payload["deterministic_fingerprint"] = canonical_sha256(seed)
    return payload


def _negotiation_refusal_payload(
    *,
    refusal_codes: List[str],
    negotiation_result: Mapping[str, object],
    requested_action_id: str,
) -> dict:
    primary_code = str((list(refusal_codes or []) or [""])[0]).strip()
    extensions = dict((dict(negotiation_result or {})).get("extensions") or {})
    validation = dict(extensions.get("validation") or {})
    missing_entitlements = _sorted_unique_strings(validation.get("missing_entitlements"))
    forbidden_process_id = str(validation.get("forbidden_process_id", "")).strip()
    if primary_code == CONTROL_REFUSAL_ENTITLEMENT_MISSING:
        return _refusal(
            CONTROL_REFUSAL_ENTITLEMENT_MISSING,
            "action requires missing entitlements",
            "Grant missing entitlements or choose an action allowed by current authority.",
            {
                "missing_entitlements": ",".join(missing_entitlements),
                "requested_action_id": str(requested_action_id),
            },
            "$.authority_context.entitlements",
        )
    if primary_code == CONTROL_REFUSAL_META_FORBIDDEN:
        return _refusal(
            CONTROL_REFUSAL_META_FORBIDDEN,
            "ranked server forbids AL4 meta control intents",
            "Use AL0-AL3 actions on ranked servers.",
            {"requested_action_id": str(requested_action_id)},
            "$.request_vector.abstraction_level_requested",
        )
    if primary_code == CONTROL_REFUSAL_VIEW_FORBIDDEN:
        return _refusal(
            CONTROL_REFUSAL_VIEW_FORBIDDEN,
            "requested view policy is forbidden",
            "Select a policy-allowed view mode for this authority context.",
            {"requested_action_id": str(requested_action_id)},
            "$.request_vector.view_requested",
        )
    if primary_code == CONTROL_REFUSAL_FIDELITY_DENIED:
        return _refusal(
            CONTROL_REFUSAL_FIDELITY_DENIED,
            "requested fidelity cannot be granted under current constraints",
            "Reduce requested fidelity or increase budget/authority as permitted.",
            {"requested_action_id": str(requested_action_id)},
            "$.request_vector.fidelity_requested",
        )
    if primary_code:
        return _refusal(
            primary_code,
            "control negotiation refused request",
            "Adjust request vector and authority/policy constraints before retrying.",
            {
                "requested_action_id": str(requested_action_id),
                "forbidden_process_id": forbidden_process_id,
            },
            "$.request_vector",
        )
    return _refusal(
        CONTROL_REFUSAL_FORBIDDEN_BY_LAW,
        "control negotiation refused request",
        "Adjust request vector and authority/policy constraints before retrying.",
        {"requested_action_id": str(requested_action_id)},
        "$.request_vector",
    )


def _decision_log_row(
    *,
    control_intent: Mapping[str, object],
    policy_ids_applied: List[str],
    input_vector: Mapping[str, object],
    negotiation_result: Mapping[str, object],
    refusal: Mapping[str, object] | None,
    emitted_intents: List[Mapping[str, object]],
    emitted_envelopes: List[Mapping[str, object]],
    emitted_commitment_ids: List[str] | None = None,
    decision_extensions: Mapping[str, object] | None = None,
) -> dict:
    intent_payload = dict(control_intent or {})
    negotiation_payload = dict(negotiation_result or {})
    resolved_vector = dict(negotiation_payload.get("resolved_vector") or {})
    downgrade_entries = [
        dict(row)
        for row in list(negotiation_payload.get("downgrade_entries") or [])
        if isinstance(row, Mapping)
    ]
    refusal_codes = _sorted_unique_strings(negotiation_payload.get("refusal_codes"))
    tick = int(max(0, _to_int((dict(control_intent or {})).get("created_tick", 0), 0)))
    intent_ids = sorted(
        str((dict(row or {})).get("intent_id", "")).strip()
        for row in list(emitted_intents or [])
        if str((dict(row or {})).get("intent_id", "")).strip()
    )
    envelope_ids = sorted(
        str((dict(row or {})).get("envelope_id", "")).strip()
        for row in list(emitted_envelopes or [])
        if str((dict(row or {})).get("envelope_id", "")).strip()
    )
    commitment_ids = _sorted_unique_strings(emitted_commitment_ids)
    downgrade_ids = _sorted_unique_strings([row.get("downgrade_id") for row in downgrade_entries])
    ir_id = str((dict(decision_extensions or {})).get("control_ir_execution", {}).get("ir_id", "")).strip()
    if not ir_id:
        ir_id = str((dict(intent_payload.get("extensions") or {})).get("control_ir_id", "")).strip()

    seed = {
        "tick": int(tick),
        "requester_subject_id": str(intent_payload.get("requester_subject_id", "")),
        "control_intent_id": str(intent_payload.get("control_intent_id", "")),
        "control_ir_id": str(ir_id),
        "policy_ids_applied": list(policy_ids_applied or []),
        "input_vector": dict(input_vector or {}),
        "resolved_vector": dict(resolved_vector or {}),
        "downgrades": list(downgrade_ids),
        "refusals": list(refusal_codes),
        "budget_allocated": int(max(0, _to_int(resolved_vector.get("budget_allocated", 0), 0))),
        "emitted_ids": {
            "intent_ids": list(intent_ids),
            "envelope_ids": list(envelope_ids),
            "commitment_ids": list(commitment_ids),
        },
        "refusal_payload": dict(refusal or {}),
    }
    decision_id = "control.decision.{}".format(canonical_sha256(seed)[:24])
    row = {
        "schema_version": "1.0.0",
        "decision_id": decision_id,
        "tick": int(tick),
        "requester_subject_id": str(intent_payload.get("requester_subject_id", "")),
        "policy_ids_applied": _sorted_unique_strings(policy_ids_applied),
        "input_vector": dict(input_vector or {}),
        "resolved_vector": dict(resolved_vector or {}),
        "downgrades": list(downgrade_ids),
        "refusals": list(refusal_codes),
        "budget_allocated": int(max(0, _to_int(resolved_vector.get("budget_allocated", 0), 0))),
        "emitted_ids": {
            "intent_ids": list(intent_ids),
            "commitment_ids": list(commitment_ids),
            "envelope_ids": list(envelope_ids),
        },
        "deterministic_fingerprint": "",
        "extensions": dict(decision_extensions or {}) | {
            "downgrade_entries": list(downgrade_entries),
            "refusal_payload": dict(refusal or {}),
        },
    }
    control_intent_id = str(intent_payload.get("control_intent_id", "")).strip()
    if control_intent_id:
        row["control_intent_id"] = control_intent_id
    if ir_id:
        row["control_ir_id"] = ir_id
    row_seed = dict(row)
    row_seed["deterministic_fingerprint"] = ""
    row["deterministic_fingerprint"] = canonical_sha256(row_seed)
    return row


def _write_decision_log(repo_root: str, log_row: Mapping[str, object]) -> str:
    repo = str(repo_root or "").strip()
    if not repo:
        return str((dict(log_row or {})).get("decision_id", ""))
    tick = int(max(0, _to_int((dict(log_row or {})).get("tick", 0), 0)))
    decision_id = str((dict(log_row or {})).get("decision_id", "")).strip()
    if not decision_id:
        decision_id = canonical_sha256(dict(log_row or {}))[:24]
    rel = os.path.join(
        "run_meta",
        "control_decisions",
        "{}.{}.json".format(int(tick), decision_id),
    )
    abs_path = os.path.join(repo, rel)
    parent = os.path.dirname(abs_path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(log_row or {})))
        handle.write("\n")
    return rel.replace("\\", "/")


def _control_proof_markers_for_decision(
    *,
    log_row: Mapping[str, object],
    control_action_id: str,
    control_policy_id: str,
) -> dict:
    payload = dict(log_row or {})
    decision_id = str(payload.get("decision_id", "")).strip()
    decision_hash = _hash64(
        payload.get("deterministic_fingerprint", ""),
        {"decision_id": decision_id, "log_row": payload},
    )
    input_vector = dict(payload.get("input_vector") or {})
    resolved_vector = dict(payload.get("resolved_vector") or {})
    ext = dict(payload.get("extensions") or {})
    downgrade_entries = [
        dict(item)
        for item in list(ext.get("downgrade_entries") or [])
        if isinstance(item, Mapping)
    ]
    abstraction_entries = sorted(
        (
            {
                "downgrade_id": str(item.get("downgrade_id", "")).strip(),
                "from_value": str(item.get("from_value", "")).strip(),
                "to_value": str(item.get("to_value", "")).strip(),
                "reason_code": str(item.get("reason_code", "")).strip(),
            }
            for item in downgrade_entries
            if str(item.get("axis", "")).strip() == "abstraction"
        ),
        key=lambda item: (
            str(item.get("downgrade_id", "")),
            str(item.get("from_value", "")),
            str(item.get("to_value", "")),
            str(item.get("reason_code", "")),
        ),
    )
    view_payload = {
        "decision_id": decision_id,
        "requested_view": str(input_vector.get("view_requested", "")).strip(),
        "resolved_view": str(resolved_vector.get("view_resolved", "")).strip(),
        "downgrade_ids": sorted(
            str(item.get("downgrade_id", "")).strip()
            for item in downgrade_entries
            if str(item.get("axis", "")).strip() == "view" and str(item.get("downgrade_id", "")).strip()
        ),
    }
    fidelity_payload = {
        "decision_id": decision_id,
        "fidelity_resolved": str(resolved_vector.get("fidelity_resolved", "")).strip(),
        "budget_allocated": int(max(0, _to_int(payload.get("budget_allocated", 0), 0))),
    }
    policy_ids = _sorted_unique_strings(payload.get("policy_ids_applied"))
    action_token = str(control_action_id or "").strip()
    policy_token = str(control_policy_id or "").strip()
    meta_payload = {
        "decision_id": decision_id,
        "is_meta_override": bool(
            action_token == "action.admin.meta_override"
            or policy_token == "ctrl.policy.admin.meta"
            or "ctrl.policy.admin.meta" in set(policy_ids)
        ),
        "control_action_id": action_token,
        "control_policy_id": policy_token,
        "policy_ids_applied": policy_ids,
    }
    return {
        "control_decision_id": decision_id,
        "control_decision_log_hash": decision_hash,
        "control_fidelity_allocation_hash": canonical_sha256(fidelity_payload),
        "control_abstraction_downgrade_hash": canonical_sha256(abstraction_entries),
        "control_view_policy_changes_hash": canonical_sha256(view_payload),
        "control_meta_override_hash": canonical_sha256(meta_payload),
    }


def _build_refused_resolution(
    *,
    control_intent_id: str,
    control_policy_id: str,
    control_action_id: str,
    resolved_vector: Mapping[str, object],
    refusal_payload: Mapping[str, object],
    downgrade_reasons: List[str],
    log_ref: str,
    proof_markers: Mapping[str, object] | None = None,
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
        "extensions": {
            "control_policy_id": str(control_policy_id),
            "control_action_id": str(control_action_id),
        },
    }
    for key, value in sorted((dict(proof_markers or {})).items(), key=lambda row: str(row[0])):
        if str(value).strip():
            resolution["extensions"][str(key)] = str(value).strip()
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
    action_template_registry: Mapping[str, object] | None = None,
    repo_root: str = "",
) -> dict:
    intent = dict(control_intent or {})
    request_vector = dict(intent.get("request_vector") or {})
    params = dict(intent.get("parameters") or {})
    authority = dict(authority_context or {})
    law = dict(law_profile or {})
    policy_context_payload = dict(policy_context or {})
    decision_log_extensions = _decision_log_extensions(policy_context_payload)
    effect_influence_payload: dict = {}
    spec_compliance_payload: dict = {}

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

    template_registry_payload = dict(action_template_registry or {})
    if not template_registry_payload:
        template_from_context = policy_context_payload.get("action_template_registry")
        if isinstance(template_from_context, Mapping):
            template_registry_payload = dict(template_from_context)
    action_template_rows = action_template_rows_by_id(template_registry_payload)
    action_template_row = dict(action_template_rows.get(action_id) or {})
    if template_registry_payload and (not action_template_row):
        refusal_payload = _refusal(
            CONTROL_REFUSAL_FORBIDDEN_BY_LAW,
            "requested action is missing action_template mapping",
            "Register requested_action_id in action_template_registry before execution.",
            {"requested_action_id": action_id},
            "$.requested_action_id",
        )
        return {"result": "refused", "refusal": refusal_payload}

    action_family_id = str(action_template_row.get("action_family_id", "")).strip()
    if action_family_id:
        decision_log_extensions = dict(decision_log_extensions)
        decision_log_extensions["action_family_id"] = action_family_id
        decision_log_extensions["action_template_id"] = str(action_template_row.get("action_template_id", "")).strip() or action_id

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
    input_vector = {
        "abstraction_level_requested": requested_al,
        "fidelity_requested": requested_fidelity,
        "view_requested": requested_view,
    }
    epistemic_requested = str(request_vector.get("epistemic_scope_requested", "")).strip()
    if epistemic_requested:
        input_vector["epistemic_scope_requested"] = epistemic_requested
    budget_requested = request_vector.get("budget_requested")
    if budget_requested is not None:
        input_vector["budget_requested"] = int(max(0, _to_int(budget_requested, 0)))

    allowed_action_patterns = _sorted_unique_strings(policy_row.get("allowed_actions"))

    produces = dict(action_row.get("produces") or {})
    process_id = str(produces.get("process_id", "")).strip() or str(params.get("process_id", "")).strip()
    task_type_id = str(produces.get("task_type_id", "")).strip()
    plan_intent_type = str(produces.get("plan_intent_type", "")).strip()
    required_capabilities = _sorted_unique_strings(action_row.get("required_capabilities"))
    required_capabilities = _sorted_unique_strings(
        list(required_capabilities) + list(_sorted_unique_strings(action_template_row.get("required_capabilities")))
    )
    required_surface_types = _sorted_unique_strings(action_template_row.get("required_surface_types"))
    required_tool_tags = _sorted_unique_strings(action_template_row.get("required_tool_tags"))
    target_entity_id = str(intent.get("target_id", "")).strip()
    effect_influence_payload = _effect_influence(
        control_intent=intent,
        policy_context=policy_context_payload,
        process_id=process_id,
    )
    if effect_influence_payload:
        decision_log_extensions = dict(decision_log_extensions)
        decision_log_extensions["effect_influence"] = dict(effect_influence_payload)
    spec_compliance_payload = _normalize_decision_extension_payload(policy_context_payload.get("spec_compliance"))
    if spec_compliance_payload:
        decision_log_extensions = dict(decision_log_extensions)
        decision_log_extensions["spec_compliance"] = dict(spec_compliance_payload)
    requester_subject_id = str(intent.get("requester_subject_id", "")).strip()
    capability_target_candidates = [token for token in (target_entity_id, requester_subject_id) if token]
    if not capability_target_candidates:
        capability_target_candidates = ["subject.unknown"]
    capability_binding_payload: object = {}
    for key in ("capability_bindings", "capability_binding_registry"):
        value = policy_context_payload.get(key)
        if isinstance(value, (dict, list)):
            capability_binding_payload = value
            break
    normalized_capability_bindings = capability_binding_rows(capability_binding_payload)
    required_process_for_law = process_id if (process_id and not task_type_id) else ""

    intent_extensions = dict(intent.get("extensions") or {})
    resolved_surface_type = str(
        intent_extensions.get("surface_type_id")
        or params.get("surface_type_id")
        or params.get("target_surface_type_id")
        or ""
    ).strip()
    if required_surface_types and (resolved_surface_type not in set(required_surface_types)):
        refusal_payload = _refusal(
            CONTROL_REFUSAL_FORBIDDEN_BY_LAW,
            "action requires surface_type incompatible with current intent",
            "Use an affordance/surface matching required_surface_types before execution.",
            {
                "requested_action_id": action_id,
                "required_surface_types": ",".join(required_surface_types),
                "surface_type_id": resolved_surface_type,
            },
            "$.extensions.surface_type_id",
        )
        return {"result": "refused", "refusal": refusal_payload}

    active_tool_tags = _sorted_unique_strings(
        list(_coerce_string_list(intent_extensions.get("active_tool_tags")))
        + list(_coerce_string_list(params.get("active_tool_tags")))
        + list(_coerce_string_list((dict(authority.get("extensions") or {})).get("held_tool_tags")))
        + list(_coerce_string_list(authority.get("held_tool_tags")))
    )
    missing_tool_tags = [tag for tag in required_tool_tags if tag not in set(active_tool_tags)]
    if missing_tool_tags:
        refusal_payload = _refusal(
            CONTROL_REFUSAL_FORBIDDEN_BY_LAW,
            "action requires tool tags not present on active tool bindings",
            "Bind/select tools that satisfy required_tool_tags before execution.",
            {
                "requested_action_id": action_id,
                "required_tool_tags": ",".join(required_tool_tags),
                "active_tool_tags": ",".join(active_tool_tags),
            },
            "$.extensions.active_tool_tags",
        )
        return {"result": "refused", "refusal": refusal_payload}

    policy_extensions = dict(policy_row.get("extensions") or {})
    negotiation_extensions = {
        "required_entitlements": _sorted_unique_strings(action_row.get("required_entitlements")),
    }
    if required_process_for_law:
        negotiation_extensions["required_process_id"] = str(required_process_for_law)
    max_fidelity = str(policy_context_payload.get("max_control_fidelity", "")).strip() or str(
        policy_extensions.get("max_control_fidelity", "")
    ).strip()
    if max_fidelity:
        negotiation_extensions["max_fidelity"] = max_fidelity
    if "budget_requested" in input_vector:
        negotiation_extensions["budget_requested"] = int(max(0, _to_int(input_vector.get("budget_requested", 0), 0)))

    submission_tick = int(max(0, _to_int(policy_context_payload.get("submission_tick", intent.get("created_tick", 0)), 0)))
    rs5_budget_state = {
        "tick": int(submission_tick),
        "max_cost_units_per_tick": int(
            max(
                0,
                _to_int(
                    policy_context_payload.get(
                        "max_control_cost_units",
                        policy_context_payload.get("rs5_budget_units", 0),
                    ),
                    0,
                ),
            )
        ),
        "runtime_budget_state": dict(policy_context_payload.get("runtime_budget_state") or {}),
        "fairness_state": dict(policy_context_payload.get("fairness_state") or {}),
    }
    connected_subject_ids = policy_context_payload.get("connected_subject_ids")
    if isinstance(connected_subject_ids, list):
        rs5_budget_state["connected_subject_ids"] = list(connected_subject_ids)

    server_profile_id = str(policy_context_payload.get("server_profile_id", "")).strip()
    negotiation_request = {
        "schema_version": "1.0.0",
        "requester_subject_id": str(intent.get("requester_subject_id", "")).strip() or "subject.unknown",
        "control_intent_id": control_intent_id,
        "request_vector": dict(input_vector),
        "context": {
            "law_profile_id": str(law.get("law_profile_id", "")).strip() or str(authority.get("law_profile_id", "")).strip() or "law.unknown",
            "server_profile_id": server_profile_id or "server.profile.local",
        },
        "extensions": negotiation_extensions,
    }
    negotiation_result = negotiate_request(
        negotiation_request=negotiation_request,
        rs5_budget_state=rs5_budget_state,
        control_policy=dict(policy_row),
        view_policy={
            "view_policy_id": requested_view,
            "allowed_view_policies": _sorted_unique_strings(policy_row.get("allowed_view_policies")),
        },
        epistemic_policy={
            "allowed_scope_ids": _sorted_unique_strings(policy_context_payload.get("allowed_scope_ids")),
            "allowed_epistemic_scopes": _sorted_unique_strings(policy_context_payload.get("allowed_epistemic_scopes")),
        },
        server_profile={"server_profile_id": server_profile_id},
        authority_context=dict(authority),
        law_profile=dict(law),
    )
    negotiation_payload = dict(negotiation_result or {})
    resolved_vector_full = dict(negotiation_payload.get("resolved_vector") or {})
    resolved_vector_full["abstraction_level_resolved"] = _al_requested(
        resolved_vector_full.get("abstraction_level_resolved", requested_al)
    )
    resolved_vector_full["fidelity_resolved"] = _fidelity_requested(
        resolved_vector_full.get("fidelity_resolved", requested_fidelity)
    )
    resolved_vector_full["view_resolved"] = str(resolved_vector_full.get("view_resolved", requested_view)).strip() or DEFAULT_VIEW_POLICY_ID
    if "budget_allocated" not in resolved_vector_full:
        resolved_vector_full["budget_allocated"] = int(max(0, _to_int(input_vector.get("budget_requested", 0), 0)))
    if effect_influence_payload:
        modifiers = dict(effect_influence_payload.get("modifiers") or {})
        visibility_modifier = dict(modifiers.get("visibility_permille") or {})
        visibility_value = int(max(0, _to_int(visibility_modifier.get("value", 0), 0)))
        if bool(visibility_modifier.get("present", False)) and visibility_value > 0:
            previous_fidelity = str(resolved_vector_full.get("fidelity_resolved", requested_fidelity)).strip() or DEFAULT_FIDELITY
            next_fidelity = previous_fidelity
            if visibility_value < 350:
                next_fidelity = "macro"
            elif visibility_value < 750 and previous_fidelity == "micro":
                next_fidelity = "meso"
            if next_fidelity != previous_fidelity:
                resolved_vector_full["fidelity_resolved"] = next_fidelity
                downgrade_entries = [
                    dict(row)
                    for row in list(negotiation_payload.get("downgrade_entries") or [])
                    if isinstance(row, Mapping)
                ]
                downgrade_seed = {
                    "control_intent_id": control_intent_id,
                    "axis": "fidelity",
                    "from_value": previous_fidelity,
                    "to_value": next_fidelity,
                    "reason_code": DOWNGRADE_EFFECT_VISIBILITY,
                    "effect_influence": effect_influence_payload,
                }
                downgrade_entry = {
                    "schema_version": "1.0.0",
                    "downgrade_id": "downgrade.effect.{}".format(canonical_sha256(downgrade_seed)[:16]),
                    "axis": "fidelity",
                    "from_value": previous_fidelity,
                    "to_value": next_fidelity,
                    "reason_code": DOWNGRADE_EFFECT_VISIBILITY,
                    "remediation_hint": "hint.effect.reduce_visibility_or_wait",
                    "extensions": {
                        "effect_ids": _sorted_unique_strings(visibility_modifier.get("applied_effect_ids")),
                        "visibility_permille": int(visibility_value),
                    },
                }
                downgrade_entries.append(downgrade_entry)
                negotiation_payload["downgrade_entries"] = sorted(
                    downgrade_entries,
                    key=lambda row: str(row.get("downgrade_id", "")),
                )
            previous_view = str(resolved_vector_full.get("view_resolved", requested_view)).strip() or DEFAULT_VIEW_POLICY_ID
            if ("freecam" in previous_view) and visibility_value < 500:
                allowed_views = _sorted_unique_strings(policy_row.get("allowed_view_policies"))
                fallback_view = DEFAULT_VIEW_POLICY_ID
                for candidate in allowed_views:
                    if "freecam" in str(candidate):
                        continue
                    fallback_view = str(candidate)
                    break
                if previous_view != fallback_view:
                    resolved_vector_full["view_resolved"] = str(fallback_view)
    negotiation_payload["resolved_vector"] = resolved_vector_full
    payload_extensions = dict(negotiation_payload.get("extensions") or {})
    if effect_influence_payload:
        payload_extensions["effect_influence"] = dict(effect_influence_payload)
    if spec_compliance_payload:
        payload_extensions["spec_compliance"] = dict(spec_compliance_payload)
    if payload_extensions:
        negotiation_payload["extensions"] = payload_extensions
    spec_bound_id = str(spec_compliance_payload.get("bound_spec_id", "")).strip()
    spec_overall_grade = str(spec_compliance_payload.get("overall_grade", "")).strip()
    spec_enforced = bool(spec_compliance_payload.get("enforce", False))
    if spec_compliance_payload and (not spec_enforced) and spec_bound_id and spec_overall_grade in {"warn", "fail"}:
        downgrade_entries = [
            dict(row)
            for row in list(negotiation_payload.get("downgrade_entries") or [])
            if isinstance(row, Mapping)
        ]
        downgrade_seed = {
            "control_intent_id": control_intent_id,
            "axis": "spec_compliance",
            "from_value": spec_overall_grade,
            "to_value": "allowed_with_warning",
            "reason_code": DOWNGRADE_SPEC_NONCOMPLIANT,
            "spec_compliance": spec_compliance_payload,
        }
        downgrade_entry = {
            "schema_version": "1.0.0",
            "downgrade_id": "downgrade.spec.{}".format(canonical_sha256(downgrade_seed)[:16]),
            "axis": "spec_compliance",
            "from_value": spec_overall_grade,
            "to_value": "allowed_with_warning",
            "reason_code": DOWNGRADE_SPEC_NONCOMPLIANT,
            "remediation_hint": "hint.spec.run_compliance_or_update_spec",
            "extensions": {
                "spec_id": spec_bound_id or None,
                "target_kind": str(spec_compliance_payload.get("target_kind", "")).strip() or None,
                "target_id": str(spec_compliance_payload.get("target_id", "")).strip() or None,
                "result_id": str(spec_compliance_payload.get("result_id", "")).strip() or None,
            },
        }
        existing_ids = set(
            str(row.get("downgrade_id", "")).strip()
            for row in downgrade_entries
            if str(row.get("downgrade_id", "")).strip()
        )
        if str(downgrade_entry.get("downgrade_id", "")).strip() not in existing_ids:
            downgrade_entries.append(downgrade_entry)
            negotiation_payload["downgrade_entries"] = sorted(
                downgrade_entries,
                key=lambda row: str(row.get("downgrade_id", "")),
            )
    seed = dict(negotiation_payload)
    seed["deterministic_fingerprint"] = ""
    negotiation_payload["deterministic_fingerprint"] = canonical_sha256(seed)

    policy_ids_applied = _policy_ids_applied(negotiation_payload, control_policy_id=control_policy_id)
    resolved_vector = {
        "abstraction_level_resolved": str(resolved_vector_full.get("abstraction_level_resolved", DEFAULT_ABSTRACTION_LEVEL)),
        "fidelity_resolved": str(resolved_vector_full.get("fidelity_resolved", DEFAULT_FIDELITY)),
        "view_resolved": str(resolved_vector_full.get("view_resolved", DEFAULT_VIEW_POLICY_ID)),
    }

    def _finalize_refusal(
        *,
        refusal_payload: Mapping[str, object],
        negotiation_for_log: Mapping[str, object],
    ) -> dict:
        log_row = _decision_log_row(
            control_intent=intent,
            policy_ids_applied=policy_ids_applied,
            input_vector=input_vector,
            negotiation_result=negotiation_for_log,
            refusal=refusal_payload,
            emitted_intents=[],
            emitted_envelopes=[],
            decision_extensions=decision_log_extensions,
        )
        log_ref = _write_decision_log(repo_root, log_row)
        proof_markers = _control_proof_markers_for_decision(
            log_row=log_row,
            control_action_id=action_id,
            control_policy_id=control_policy_id,
        )
        return {
            "result": "refused",
            "resolution": _build_refused_resolution(
                control_intent_id=control_intent_id,
                control_policy_id=control_policy_id,
                control_action_id=action_id,
                resolved_vector=resolved_vector,
                refusal_payload=refusal_payload,
                downgrade_reasons=_negotiation_downgrade_reasons(negotiation_for_log),
                log_ref=log_ref,
                proof_markers=proof_markers,
            ),
            "refusal": dict(refusal_payload),
        }

    if spec_compliance_payload and spec_enforced and spec_bound_id:
        spec_compliance_available = bool(spec_compliance_payload.get("compliance_available", False))
        if not spec_compliance_available:
            refusal_payload = _refusal(
                CONTROL_REFUSAL_SPEC_NONCOMPLIANT,
                "spec compliance evidence is required by policy before execution",
                "Run process.spec_check_compliance for the bound spec target, then retry execution.",
                {
                    "spec_id": spec_bound_id,
                    "target_kind": str(spec_compliance_payload.get("target_kind", "")).strip(),
                    "target_id": str(spec_compliance_payload.get("target_id", "")).strip(),
                },
                "$.target_id",
            )
            return _finalize_refusal(
                refusal_payload=refusal_payload,
                negotiation_for_log=_negotiation_with_refusal_code(
                    negotiation_payload,
                    CONTROL_REFUSAL_SPEC_NONCOMPLIANT,
                ),
            )
        if spec_overall_grade == "fail":
            refusal_payload = _refusal(
                CONTROL_REFUSAL_SPEC_NONCOMPLIANT,
                "target is noncompliant with enforced bound spec",
                "Adjust the target/spec and rerun compliance checks before retrying execution.",
                {
                    "spec_id": spec_bound_id,
                    "target_kind": str(spec_compliance_payload.get("target_kind", "")).strip(),
                    "target_id": str(spec_compliance_payload.get("target_id", "")).strip(),
                    "result_id": str(spec_compliance_payload.get("result_id", "")).strip(),
                },
                "$.target_id",
            )
            return _finalize_refusal(
                refusal_payload=refusal_payload,
                negotiation_for_log=_negotiation_with_refusal_code(
                    negotiation_payload,
                    CONTROL_REFUSAL_SPEC_NONCOMPLIANT,
                ),
            )

    if required_capabilities:
        if not normalized_capability_bindings:
            missing_target = str(target_entity_id or requester_subject_id)
            refusal_payload = _refusal(
                CONTROL_REFUSAL_FORBIDDEN_BY_LAW,
                "required capabilities cannot be validated because capability bindings are unavailable",
                "Provide capability_bindings in policy context and bind required capabilities before retrying.",
                {
                    "requested_action_id": action_id,
                    "target_id": missing_target,
                    "required_capabilities": ",".join(required_capabilities),
                },
                "$.policy_context.capability_bindings",
            )
            return _finalize_refusal(
                refusal_payload=refusal_payload,
                negotiation_for_log=_negotiation_with_refusal_code(negotiation_payload, CONTROL_REFUSAL_FORBIDDEN_BY_LAW),
            )
        capability_satisfied = False
        missing_by_target: Dict[str, List[str]] = {}
        for candidate_id in capability_target_candidates:
            missing = resolve_missing_capabilities(
                entity_id=str(candidate_id),
                required_capabilities=required_capabilities,
                capability_bindings=normalized_capability_bindings,
            )
            if not missing:
                capability_satisfied = True
                break
            missing_by_target[str(candidate_id)] = list(missing)
        if not capability_satisfied:
            missing_target = sorted(missing_by_target.keys())[0] if missing_by_target else str(target_entity_id or requester_subject_id)
            missing_caps = list(missing_by_target.get(missing_target) or required_capabilities)
            refusal_payload = _refusal(
                CONTROL_REFUSAL_FORBIDDEN_BY_LAW,
                "target is missing required capabilities for requested action",
                "Bind required capabilities to the target entity before retrying this action.",
                {
                    "requested_action_id": action_id,
                    "target_id": missing_target,
                    "required_capabilities": ",".join(missing_caps),
                },
                "$.target_id",
            )
            return _finalize_refusal(
                refusal_payload=refusal_payload,
                negotiation_for_log=_negotiation_with_refusal_code(negotiation_payload, CONTROL_REFUSAL_FORBIDDEN_BY_LAW),
            )

    refusal_codes = [str(item).strip() for item in list(negotiation_payload.get("refusal_codes") or []) if str(item).strip()]
    if refusal_codes:
        refusal_payload = _negotiation_refusal_payload(
            refusal_codes=refusal_codes,
            negotiation_result=negotiation_payload,
            requested_action_id=action_id,
        )
        return _finalize_refusal(refusal_payload=refusal_payload, negotiation_for_log=negotiation_payload)

    if effect_influence_payload:
        modifiers = dict(effect_influence_payload.get("modifiers") or {})
        access_modifier = dict(modifiers.get("access_restricted") or {})
        restricted_process_ids = {
            "process.portal_open",
            "process.portal_close",
            "process.portal_lock",
            "process.portal_unlock",
            "process.portal_seal_breach",
            "process.hatch_open",
            "process.hatch_close",
            "process.vent_open",
            "process.vent_close",
            "process.vent_activate",
        }
        access_restricted = bool(access_modifier.get("present", False)) and int(
            max(0, _to_int(access_modifier.get("value", 0), 0))
        ) > 0
        if access_restricted and process_id in restricted_process_ids:
            refusal_payload = _refusal(
                REFUSAL_EFFECT_FORBIDDEN,
                "target is currently access restricted by active effects",
                "Wait for effect expiration or remove effect through process.effect_remove with lawful authority.",
                {
                    "requested_action_id": action_id,
                    "target_id": target_entity_id,
                    "effect_ids": ",".join(_sorted_unique_strings(access_modifier.get("applied_effect_ids"))),
                },
                "$.target_id",
            )
            return _finalize_refusal(
                refusal_payload=refusal_payload,
                negotiation_for_log=_negotiation_with_refusal_code(negotiation_payload, REFUSAL_EFFECT_FORBIDDEN),
            )

    if allowed_action_patterns and (not _path_allowed(action_id, allowed_action_patterns)):
        refusal_payload = _refusal(
            CONTROL_REFUSAL_FORBIDDEN_BY_LAW,
            "action is not allowed by control policy",
            "Use an action listed in control policy or switch policy under lawful authority.",
            {"requested_action_id": action_id, "control_policy_id": control_policy_id},
            "$.requested_action_id",
        )
        return _finalize_refusal(
            refusal_payload=refusal_payload,
            negotiation_for_log=_negotiation_with_refusal_code(negotiation_payload, CONTROL_REFUSAL_FORBIDDEN_BY_LAW),
        )

    if bool(policy_extensions.get("replay_only", False)):
        replay_action_allowed = (
            str(action_id) == "action.view.change"
            or str(action_id) == "action.view.change_policy"
            or str(action_id).startswith("action.replay.")
            or str(action_id) == "action.fidelity.request"
        )
        replay_process_allowed = _replay_read_only_process_allowed(process_id)
        if (not replay_action_allowed) or (not replay_process_allowed) or bool(task_type_id) or bool(plan_intent_type):
            refusal_payload = _refusal(
                CONTROL_REFUSAL_REPLAY_MUTATION_FORBIDDEN,
                "replay mode only permits read-only view/fidelity/reenactment control",
                "Use action.view.change or replay-safe action/process while replay policy is active.",
                {
                    "requested_action_id": action_id,
                    "process_id": process_id,
                    "control_policy_id": control_policy_id,
                },
                "$.requested_action_id",
            )
            return _finalize_refusal(
                refusal_payload=refusal_payload,
                negotiation_for_log=_negotiation_with_refusal_code(
                    negotiation_payload,
                    CONTROL_REFUSAL_REPLAY_MUTATION_FORBIDDEN,
                ),
            )

    emitted_intents: List[dict] = []
    if plan_intent_type and str(resolved_vector.get("abstraction_level_resolved", "")) in ("AL0", "AL1", "AL2"):
        refusal_payload = _refusal(
            CONTROL_REFUSAL_PLANNING_ONLY,
            "planning actions are derived-only at current abstraction",
            "Request AL3 planning abstraction or switch to executable action.",
            {"requested_action_id": action_id, "plan_intent_type": plan_intent_type},
            "$.requested_action_id",
        )
        return _finalize_refusal(
            refusal_payload=refusal_payload,
            negotiation_for_log=_negotiation_with_refusal_code(negotiation_payload, CONTROL_REFUSAL_PLANNING_ONLY),
        )

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
            return _finalize_refusal(
                refusal_payload=refusal_payload,
                negotiation_for_log=_negotiation_with_refusal_code(negotiation_payload, CONTROL_REFUSAL_FORBIDDEN_BY_LAW),
            )
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
        policy_ids_applied=policy_ids_applied,
        input_vector=input_vector,
        negotiation_result=negotiation_payload,
        refusal=None,
        emitted_intents=emitted_intents,
        emitted_envelopes=emitted_envelopes,
        decision_extensions=decision_log_extensions,
    )
    log_ref = _write_decision_log(repo_root, log_row)
    proof_markers = _control_proof_markers_for_decision(
        log_row=log_row,
        control_action_id=action_id,
        control_policy_id=control_policy_id,
    )
    emitted_envelopes = [
        dict(row)
        for row in list(emitted_envelopes or [])
        if isinstance(row, Mapping)
    ]
    for envelope_row in emitted_envelopes:
        ext = dict(envelope_row.get("extensions") or {})
        for key, value in sorted(proof_markers.items(), key=lambda row: str(row[0])):
            if str(value).strip():
                ext[str(key)] = str(value).strip()
        envelope_row["extensions"] = ext
    downgrade_reasons = _negotiation_downgrade_reasons(negotiation_payload)

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
            "policy_ids_applied": policy_ids_applied,
            "negotiation_fingerprint": str(negotiation_payload.get("deterministic_fingerprint", "")).strip(),
            "effect_influence_fingerprint": str(effect_influence_payload.get("deterministic_fingerprint", "")).strip(),
        }
        | dict((str(key), str(value).strip()) for key, value in sorted(proof_markers.items(), key=lambda row: str(row[0])) if str(value).strip()),
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
