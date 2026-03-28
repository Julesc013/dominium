"""Deterministic interaction dispatch via intent envelopes and process execution."""

from __future__ import annotations

import json
import os
from typing import Dict, List

from net.anti_cheat.anti_cheat_engine import (
    check_authority_integrity,
    check_input_integrity,
)
from net.policies.policy_lockstep import POLICY_ID_LOCKSTEP
from net.policies.policy_server_authoritative import POLICY_ID_SERVER_AUTHORITATIVE
from net.policies.policy_srz_hybrid import POLICY_ID_SRZ_HYBRID
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.sessionx.boundary_debug import debug_assert_after_execute
from control import build_control_intent, build_control_resolution
from interaction.task import resolve_task_type_for_completion_process

from .affordance_generator import build_affordance_list
from .inspection_overlays import build_inspection_overlays
from .interaction_panel import build_interaction_panel, build_selection_overlay
from .preview_generator import generate_interaction_preview


_DEFAULT_INTERACTION_MAX_PER_TICK = 24


def _sorted_unique_strings(values: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in (values or []) if str(item).strip()))


def _read_decision_log_payload(repo_root: str, decision_log_ref: str) -> dict:
    repo = str(repo_root or "").strip()
    rel = str(decision_log_ref or "").strip()
    if not repo or not rel:
        return {}
    abs_path = os.path.join(repo, rel.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def _reason_token(reason_code: str) -> str:
    token = str(reason_code or "").strip()
    if not token:
        return ""
    return token.split(".")[-1]


def _decision_log_ui_messages(decision_log_payload: dict) -> List[dict]:
    payload = dict(decision_log_payload or {})
    if not payload:
        return []
    ext = dict(payload.get("extensions") or {})
    downgrade_entries = [
        dict(item)
        for item in list(ext.get("downgrade_entries") or [])
        if isinstance(item, dict)
    ]
    downgrade_entries = sorted(
        downgrade_entries,
        key=lambda item: (
            str(item.get("axis", "")),
            str(item.get("from_value", "")),
            str(item.get("to_value", "")),
            str(item.get("reason_code", "")),
            str(item.get("downgrade_id", "")),
        ),
    )
    out: List[dict] = []
    for row in downgrade_entries:
        axis = str(row.get("axis", "")).strip()
        from_value = str(row.get("from_value", "")).strip()
        to_value = str(row.get("to_value", "")).strip()
        reason_code = str(row.get("reason_code", "")).strip()
        reason_token = _reason_token(reason_code)
        if axis == "fidelity":
            message = "Requested {} fidelity downgraded to {} ({}).".format(
                from_value or "unknown",
                to_value or "unknown",
                reason_token or "downgrade",
            )
        else:
            message = "Requested {} {} downgraded to {} ({}).".format(
                axis or "setting",
                from_value or "unknown",
                to_value or "unknown",
                reason_token or "downgrade",
            )
        out.append(
            {
                "kind": "downgrade",
                "axis": axis,
                "reason_code": reason_code,
                "message": message,
                "remediation_hint": str(row.get("remediation_hint", "")).strip(),
            }
        )
    refusals = _sorted_unique_strings(payload.get("refusals"))
    if refusals:
        refusal_payload = dict(ext.get("refusal_payload") or {})
        reason_code = str(refusals[0]).strip()
        message = str(refusal_payload.get("message", "")).strip() or "control request refused ({})".format(reason_code)
        out.append(
            {
                "kind": "refusal",
                "reason_code": reason_code,
                "message": message,
                "remediation_hint": str(refusal_payload.get("remediation_hint", "")).strip(),
            }
        )
    return out


def _registry_payload(policy_context: dict | None, key: str) -> dict:
    return dict((dict(policy_context or {})).get(str(key), {}) or {})


def _registry_payload_with_fallback(
    *,
    policy_context: dict | None,
    key: str,
    repo_root: str,
    registry_rel_path: str,
) -> dict:
    payload = _registry_payload(policy_context, key)
    if payload:
        return payload
    root = str(repo_root or "").strip()
    if not root:
        return {}
    abs_path = os.path.join(root, str(registry_rel_path).replace("/", os.sep))
    try:
        loaded = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(loaded, dict):
        return {}
    return dict(loaded.get("record") or loaded)


def _held_tool_tags(policy_context: dict | None) -> List[object]:
    return list((dict(policy_context or {})).get("held_tool_tags") or [])


def _active_tool_context(state: dict | None, authority_context: dict | None, policy_context: dict | None) -> dict:
    state_payload = dict(state or {})
    authority = dict(authority_context or {})
    policy = dict(policy_context or {})
    candidates = []
    for token in (
        authority.get("subject_id"),
        authority.get("agent_id"),
        authority.get("controller_id"),
        (dict(authority.get("extensions") or {})).get("subject_id"),
        (dict(authority.get("extensions") or {})).get("agent_id"),
        (dict(authority.get("extensions") or {})).get("controller_id"),
        policy.get("active_subject_id"),
        policy.get("active_agent_id"),
        policy.get("active_controller_id"),
    ):
        candidate = str(token or "").strip()
        if candidate and candidate not in candidates:
            candidates.append(candidate)
    tool_bindings = [
        dict(item)
        for item in list(state_payload.get("tool_bindings") or [])
        if isinstance(item, dict) and bool(item.get("active", False))
    ]
    tool_bindings = sorted(
        tool_bindings,
        key=lambda item: (
            str(item.get("subject_id", "")),
            str(item.get("bind_id", "")),
            str(item.get("tool_id", "")),
        ),
    )
    active_binding = {}
    for subject_id in candidates:
        for row in tool_bindings:
            if str(row.get("subject_id", "")).strip() == subject_id:
                active_binding = dict(row)
                break
        if active_binding:
            break
    if not active_binding and tool_bindings:
        active_binding = dict(tool_bindings[0])

    tool_rows = [
        dict(item)
        for item in list(state_payload.get("tool_assemblies") or [])
        if isinstance(item, dict)
    ]
    tool_rows = sorted(tool_rows, key=lambda item: str(item.get("tool_id", "")))
    active_tool_id = str(active_binding.get("tool_id", "")).strip()
    active_tool_row = {}
    for row in tool_rows:
        if str(row.get("tool_id", "")).strip() == active_tool_id:
            active_tool_row = dict(row)
            break

    if not active_tool_row:
        explicit = dict(policy.get("active_tool") or {})
        if str(explicit.get("tool_id", "")).strip():
            active_tool_row = explicit
            active_tool_id = str(explicit.get("tool_id", "")).strip()

    if not active_tool_row:
        return {}

    tool_tags = sorted(
        set(
            str(item).strip()
            for item in list(active_tool_row.get("tool_tags") or [])
            if str(item).strip()
        )
    )
    return {
        "tool_id": active_tool_id,
        "tool_type_id": str(active_tool_row.get("tool_type_id", "")).strip(),
        "effect_model_id": str(active_tool_row.get("effect_model_id", "")).strip(),
        "tool_tags": tool_tags,
        "subject_id": str(active_binding.get("subject_id", "")).strip() or None,
    }


def _hash64(token: str, fallback_seed: object) -> str:
    value = str(token or "").strip()
    if len(value) == 64 and all(ch in "0123456789abcdefABCDEF" for ch in value):
        return value.lower()
    return canonical_sha256(fallback_seed)


def _to_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _canonical_parameters(payload: object):
    if isinstance(payload, dict):
        return dict((str(key), _canonical_parameters(payload[key])) for key in sorted(payload.keys()))
    if isinstance(payload, list):
        return [_canonical_parameters(item) for item in payload]
    if payload is None:
        return None
    if isinstance(payload, (str, int, float, bool)):
        return payload
    return str(payload)


def _mp_policy_id(policy_context: dict | None) -> str:
    payload = dict(policy_context or {})
    return (
        str(payload.get("net_policy_id", "")).strip()
        or str(payload.get("policy_id", "")).strip()
        or str(payload.get("multiplayer_policy_id", "")).strip()
    )


def _policy_submission_tick(
    *,
    policy_context: dict | None,
    current_tick: int,
    requested_submission_tick: int,
) -> int:
    policy_id = _mp_policy_id(policy_context)
    requested = int(max(0, _to_int(requested_submission_tick, current_tick)))
    base_tick = int(max(0, _to_int(current_tick, 0)))
    if policy_id == POLICY_ID_LOCKSTEP:
        lead = max(1, _to_int((dict(policy_context or {})).get("lockstep_intent_lead_ticks", 1), 1))
        return int(max(requested, base_tick + int(lead)))
    if policy_id == POLICY_ID_SERVER_AUTHORITATIVE:
        return int(max(requested, base_tick))
    if policy_id == POLICY_ID_SRZ_HYBRID:
        return int(max(requested, base_tick))
    return int(max(requested, base_tick))


def _authority_peer_id(authority_context: dict | None, fallback: str = "peer.local") -> str:
    payload = dict(authority_context or {})
    token = str(payload.get("peer_id", "")).strip()
    if token:
        return token
    return str(fallback or "peer.local")


def _anti_cheat_runtime(policy_context: dict | None) -> dict | None:
    payload = dict(policy_context or {})
    runtime = payload.get("anti_cheat_runtime")
    if isinstance(runtime, dict):
        return runtime
    return None


def _record_input_violation(
    *,
    repo_root: str,
    policy_context: dict | None,
    authority_context: dict,
    tick: int,
    reason_code: str,
    evidence: list[str],
) -> dict:
    runtime = _anti_cheat_runtime(policy_context)
    if not runtime:
        return {}
    if not str(repo_root).strip():
        return {}
    return check_input_integrity(
        repo_root=str(repo_root),
        runtime=runtime,
        tick=int(tick),
        peer_id=_authority_peer_id(authority_context),
        valid=False,
        reason_code=str(reason_code),
        evidence=[str(item) for item in list(evidence or [])],
        default_action_token="refuse",
    )


def _record_authority_violation(
    *,
    repo_root: str,
    policy_context: dict | None,
    authority_context: dict,
    tick: int,
    reason_code: str,
    evidence: list[str],
) -> dict:
    runtime = _anti_cheat_runtime(policy_context)
    if not runtime:
        return {}
    if not str(repo_root).strip():
        return {}
    return check_authority_integrity(
        repo_root=str(repo_root),
        runtime=runtime,
        tick=int(tick),
        peer_id=_authority_peer_id(authority_context),
        allowed=False,
        reason_code=str(reason_code),
        evidence=[str(item) for item in list(evidence or [])],
        default_action_token="refuse",
    )


def _check_interaction_rate_limit(
    *,
    policy_context: dict | None,
    authority_context: dict,
    tick: int,
) -> Dict[str, object]:
    payload = dict(policy_context or {})
    state = dict(payload.get("interaction_spam_state") or {})
    max_per_tick = max(1, _to_int(payload.get("interaction_max_per_tick", _DEFAULT_INTERACTION_MAX_PER_TICK), _DEFAULT_INTERACTION_MAX_PER_TICK))
    peer_id = _authority_peer_id(authority_context)
    key = "{}|{}".format(peer_id, int(tick))
    count = int(max(0, _to_int(state.get(key, 0), 0))) + 1
    state[key] = count
    if isinstance(policy_context, dict):
        policy_context["interaction_spam_state"] = dict((str(k), int(max(0, _to_int(v, 0)))) for k, v in sorted(state.items()))
    if count <= max_per_tick:
        return {"result": "complete"}
    return _refusal(
        "refusal.net.input_rate_exceeded",
        "interaction intent rate exceeded deterministic per-tick limit",
        "Throttle interaction submissions or increase interaction_max_per_tick in server policy.",
        {"peer_id": peer_id, "tick": str(tick), "max_per_tick": str(max_per_tick)},
        "$.interaction",
    )


def _refusal(
    reason_code: str,
    message: str,
    remediation_hint: str,
    relevant_ids: Dict[str, object] | None = None,
    path: str = "$",
) -> Dict[str, object]:
    ids = {}
    for key, value in sorted((dict(relevant_ids or {})).items(), key=lambda row: str(row[0])):
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
        },
        "errors": [
            {
                "code": str(reason_code),
                "message": str(message),
                "path": str(path),
            }
        ],
    }


def select_target(
    *,
    perceived_model: dict,
    target_semantic_id: str,
) -> Dict[str, object]:
    token = str(target_semantic_id).strip()
    if not token:
        return _refusal(
            "refusal.interaction.target_missing",
            "target semantic id is required",
            "Provide a semantic id from PerceivedModel entities/populations.",
            {},
            "$.target_semantic_id",
        )

    entity_ids = []
    for row in sorted((item for item in list((dict((dict(perceived_model or {})).get("entities") or {})).get("entries") or []) if isinstance(item, dict)), key=lambda item: str(item.get("entity_id", ""))):
        entity_id = str(row.get("semantic_id", "")).strip() or str(row.get("entity_id", "")).strip()
        if entity_id:
            entity_ids.append(entity_id)
    population_ids = []
    for row in sorted((item for item in list((dict((dict(perceived_model or {})).get("populations") or {})).get("entries") or []) if isinstance(item, dict)), key=lambda item: str(item.get("cohort_id", ""))):
        cohort_id = str(row.get("cohort_id", "")).strip()
        population_id = str(row.get("population_id", "")).strip()
        if cohort_id:
            population_ids.append(cohort_id)
        if population_id:
            population_ids.append(population_id)
    known_ids = set(_sorted_unique_strings(entity_ids + population_ids))
    if token not in known_ids:
        return _refusal(
            "refusal.interaction.target_unknown",
            "target semantic id is not visible in current PerceivedModel",
            "Select a visible semantic id from observed entities or populations.",
            {"target_semantic_id": token},
            "$.target_semantic_id",
        )
    return {
        "result": "complete",
        "target_semantic_id": token,
    }


def _find_affordance(affordance_list: dict, affordance_id: str) -> dict:
    token = str(affordance_id).strip()
    rows = list((dict(affordance_list or {})).get("affordances") or [])
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("affordance_id", ""))):
        if str(row.get("affordance_id", "")).strip() == token:
            return dict(row)
    return {}


def build_interaction_control_intent(
    *,
    affordance_row: dict,
    parameters: dict,
    authority_context: dict,
    policy_context: dict | None = None,
    tick: int,
) -> Dict[str, object]:
    process_id = str((dict(affordance_row or {})).get("process_id", "")).strip()
    affordance_id = str((dict(affordance_row or {})).get("affordance_id", "")).strip()
    if (not process_id) or (not affordance_id):
        return _refusal(
            "refusal.interaction.affordance_invalid",
            "affordance row is missing process_id or affordance_id",
            "Regenerate affordance list and retry interaction execute.",
            {},
            "$.affordance",
        )
    canonical_parameters = _canonical_parameters(dict(parameters or {}))
    if not isinstance(canonical_parameters, dict):
        canonical_parameters = {}
    extensions = dict((dict(affordance_row or {})).get("extensions") or {})
    active_tool_effect_parameters = dict(extensions.get("active_tool_effect_parameters") or {})
    if active_tool_effect_parameters and "tool_effect" not in canonical_parameters:
        canonical_parameters["tool_effect"] = _canonical_parameters(active_tool_effect_parameters)
    active_tool_id = str(extensions.get("active_tool_id", "")).strip()
    if active_tool_id and "tool_id" not in canonical_parameters:
        canonical_parameters["tool_id"] = active_tool_id
    active_tool_type_id = str(extensions.get("active_tool_type_id", "")).strip()
    if active_tool_type_id and "tool_type_id" not in canonical_parameters:
        canonical_parameters["tool_type_id"] = active_tool_type_id
    active_tool_effect_model_id = str(extensions.get("active_tool_effect_model_id", "")).strip()
    if active_tool_effect_model_id and "tool_effect_model_id" not in canonical_parameters:
        canonical_parameters["tool_effect_model_id"] = active_tool_effect_model_id
    active_tool_tags = _sorted_unique_strings(list(extensions.get("active_tool_tags") or []))
    if active_tool_tags and "active_tool_tags" not in canonical_parameters:
        canonical_parameters["active_tool_tags"] = list(active_tool_tags)

    surface_id = str(extensions.get("surface_id", "")).strip()
    surface_type_id = str(extensions.get("surface_type_id", "")).strip()
    target_semantic_id = str((dict(affordance_row or {})).get("target_semantic_id", "")).strip()
    task_type_registry = _registry_payload(policy_context, "task_type_registry")
    task_type_row = resolve_task_type_for_completion_process(
        completion_process_id=process_id,
        surface_type_id=surface_type_id,
        task_type_registry=task_type_registry,
    )
    dispatch_process_id = process_id
    if task_type_row and surface_id:
        dispatch_process_id = "process.task_create"
        if "task_type_id" not in canonical_parameters:
            canonical_parameters["task_type_id"] = str(task_type_row.get("task_type_id", "")).strip()
        if "process_id_to_execute" not in canonical_parameters:
            canonical_parameters["process_id_to_execute"] = process_id
        if "target_semantic_id" not in canonical_parameters and target_semantic_id:
            canonical_parameters["target_semantic_id"] = target_semantic_id
        if "surface_id" not in canonical_parameters:
            canonical_parameters["surface_id"] = surface_id
        if "surface_type_id" not in canonical_parameters and surface_type_id:
            canonical_parameters["surface_type_id"] = surface_type_id
        actor_subject_id = str(
            canonical_parameters.get("actor_subject_id")
            or canonical_parameters.get("subject_id")
            or canonical_parameters.get("agent_id")
            or canonical_parameters.get("controller_id")
            or (dict(authority_context or {})).get("subject_id")
            or (dict(authority_context or {})).get("agent_id")
            or (dict(authority_context or {})).get("controller_id")
            or (dict(authority_context or {})).get("peer_id")
            or ""
        ).strip()
        if actor_subject_id:
            canonical_parameters["actor_subject_id"] = actor_subject_id
    action_id = str((dict(extensions).get("control_action_id", ""))).strip()
    if not action_id:
        action_id = "action.surface.execute_task" if task_type_row and surface_id else "action.interaction.execute_process"
    control_parameters = dict(canonical_parameters)
    control_parameters["process_id"] = dispatch_process_id
    control_intent = build_control_intent(
        requester_subject_id=str(
            (dict(authority_context or {})).get("subject_id")
            or (dict(authority_context or {})).get("agent_id")
            or (dict(authority_context or {})).get("controller_id")
            or (dict(authority_context or {})).get("peer_id")
            or "subject.unknown"
        ).strip(),
        requested_action_id=action_id,
        target_kind=str((dict(extensions).get("target_kind", ""))).strip() or "surface",
        target_id=target_semantic_id or None,
        parameters=control_parameters,
        abstraction_level_requested=str((dict(policy_context or {})).get("abstraction_level_requested", "AL0")),
        fidelity_requested=str((dict(policy_context or {})).get("fidelity_requested", "meso")),
        view_requested=str((dict(policy_context or {})).get("view_requested", "")) or "view.mode.first_person",
        inspection_requested=str((dict(policy_context or {})).get("inspection_requested", "none")),
        reenactment_requested=str((dict(policy_context or {})).get("reenactment_requested", "none")),
        created_tick=int(max(0, _to_int(tick, 0))),
    )
    control_extensions = dict(control_intent.get("extensions") or {})
    control_extensions["affordance_id"] = affordance_id
    control_extensions["surface_id"] = surface_id or None
    control_extensions["surface_type_id"] = surface_type_id or None
    control_extensions["completion_process_id"] = process_id
    control_extensions["task_type_id"] = str(task_type_row.get("task_type_id", "")).strip() or None
    control_extensions["interaction_action_id"] = str((dict(extensions).get("action_id", "")).strip() or None)
    control_extensions["active_tool_id"] = active_tool_id or None
    control_extensions["active_tool_type_id"] = active_tool_type_id or None
    control_extensions["active_tool_effect_model_id"] = active_tool_effect_model_id or None
    control_extensions["active_tool_tags"] = list(active_tool_tags)
    control_extensions["authority_context_ref"] = {
        "authority_origin": str((dict(authority_context or {})).get("authority_origin", "")),
        "law_profile_id": str((dict(authority_context or {})).get("law_profile_id", "")),
    }
    control_intent["extensions"] = control_extensions
    control_intent["deterministic_fingerprint"] = canonical_sha256(
        dict(control_intent, deterministic_fingerprint="")
    )
    return {
        "result": "complete",
        "control_intent": control_intent,
    }


def execute_affordance(
    *,
    state: dict,
    affordance_list: dict,
    affordance_id: str,
    parameters: dict,
    law_profile: dict,
    authority_context: dict,
    navigation_indices: dict | None = None,
    policy_context: dict | None = None,
    peer_id: str = "",
    deterministic_sequence_number: int = 0,
    submission_tick: int = 0,
    source_shard_id: str = "shard.0",
    target_shard_id: str = "shard.0",
    repo_root: str = "",
) -> Dict[str, object]:
    affordance_row = _find_affordance(affordance_list=affordance_list, affordance_id=affordance_id)
    if not affordance_row:
        _record_input_violation(
            repo_root=repo_root,
            policy_context=policy_context,
            authority_context=authority_context,
            tick=int(max(0, _to_int((dict((dict(state or {})).get("simulation_time") or {})).get("tick", 0), 0))),
            reason_code="refusal.interaction.affordance_unknown",
            evidence=["interaction execute requested unknown affordance id"],
        )
        return _refusal(
            "refusal.interaction.affordance_unknown",
            "requested affordance_id is not present in deterministic affordance list",
            "Refresh affordance list for the selected target and retry.",
            {"affordance_id": str(affordance_id)},
            "$.affordance_id",
        )

    extensions = dict(affordance_row.get("extensions") or {})
    if not bool(extensions.get("enabled", False)):
        missing_entitlements = _sorted_unique_strings(list(extensions.get("missing_entitlements") or []))
        missing_channels = _sorted_unique_strings(list(extensions.get("missing_lens_channels") or []))
        reason_code = "refusal.interaction.affordance_disabled"
        if missing_entitlements:
            reason_code = "ENTITLEMENT_MISSING"
        elif missing_channels:
            reason_code = "refusal.ep.channel_forbidden"
        _record_authority_violation(
            repo_root=repo_root,
            policy_context=policy_context,
            authority_context=authority_context,
            tick=int(max(0, _to_int((dict((dict(state or {})).get("simulation_time") or {})).get("tick", 0), 0))),
            reason_code=str(reason_code),
            evidence=["interaction execute attempted disabled affordance"],
        )
        return _refusal(
            reason_code,
            "selected affordance is disabled for current law/authority/lens context",
            "Grant missing entitlements/channels or choose an enabled affordance.",
            {
                "affordance_id": str(affordance_id),
                "missing_entitlements": ",".join(missing_entitlements),
                "missing_lens_channels": ",".join(missing_channels),
            },
            "$.affordance_id",
        )

    tick = int(max(0, _to_int((dict((dict(state or {})).get("simulation_time") or {})).get("tick", 0), 0)))
    rate_limit = _check_interaction_rate_limit(
        policy_context=policy_context,
        authority_context=authority_context,
        tick=tick,
    )
    if str(rate_limit.get("result", "")) != "complete":
        _record_input_violation(
            repo_root=repo_root,
            policy_context=policy_context,
            authority_context=authority_context,
            tick=int(tick),
            reason_code="refusal.net.input_rate_exceeded",
            evidence=["interaction spam threshold exceeded"],
        )
        return rate_limit
    built_control_intent = build_interaction_control_intent(
        affordance_row=affordance_row,
        parameters=dict(parameters or {}),
        authority_context=dict(authority_context or {}),
        policy_context=policy_context,
        tick=tick,
    )
    if str(built_control_intent.get("result", "")) != "complete":
        return built_control_intent
    control_intent = dict(built_control_intent.get("control_intent") or {})

    policy_id = _mp_policy_id(policy_context)
    active_shard_id = str((dict(policy_context or {})).get("active_shard_id", "shard.0")).strip() or "shard.0"
    source_shard = str(source_shard_id or active_shard_id).strip() or active_shard_id
    target_shard = str(target_shard_id or source_shard).strip() or source_shard
    if policy_id == POLICY_ID_SRZ_HYBRID and source_shard != target_shard:
        _record_authority_violation(
            repo_root=repo_root,
            policy_context=policy_context,
            authority_context=authority_context,
            tick=int(tick),
            reason_code="refusal.civ.order_cross_shard_not_supported",
            evidence=["interaction target shard differs from source shard under hybrid policy"],
        )
        return _refusal(
            "refusal.civ.order_cross_shard_not_supported",
            "cross-shard interaction dispatch is not supported by current hybrid routing path",
            "Route interaction to local shard target or split into deterministic shard-local commands.",
            {"source_shard_id": source_shard, "target_shard_id": target_shard},
            "$.target_shard_id",
        )

    control_policy_context = dict(policy_context or {})
    control_policy_context["peer_id"] = str(peer_id or "")
    control_policy_context["deterministic_sequence_number"] = int(max(0, _to_int(deterministic_sequence_number, 0)))
    control_policy_context["submission_tick"] = _policy_submission_tick(
        policy_context=policy_context,
        current_tick=int(tick),
        requested_submission_tick=int(max(0, _to_int(submission_tick, tick))),
    )
    control_policy_context["source_shard_id"] = source_shard
    control_policy_context["target_shard_id"] = target_shard
    control_policy_context["effect_rows"] = [
        dict(row)
        for row in list((dict(state or {})).get("effect_rows") or [])
        if isinstance(row, dict)
    ]
    control_policy_context["effect_type_registry"] = _registry_payload_with_fallback(
        policy_context=policy_context,
        key="effect_type_registry",
        repo_root=repo_root,
        registry_rel_path="data/registries/effect_type_registry.json",
    )
    control_policy_context["stacking_policy_registry"] = _registry_payload_with_fallback(
        policy_context=policy_context,
        key="stacking_policy_registry",
        repo_root=repo_root,
        registry_rel_path="data/registries/stacking_policy_registry.json",
    )
    control_resolution = build_control_resolution(
        control_intent=dict(control_intent),
        law_profile=dict(law_profile or {}),
        authority_context=dict(authority_context or {}),
        policy_context=control_policy_context,
        control_action_registry=_registry_payload(policy_context, "control_action_registry"),
        control_policy_registry=_registry_payload(policy_context, "control_policy_registry"),
        action_template_registry=_registry_payload(policy_context, "action_template_registry"),
        repo_root=repo_root,
    )
    resolution = dict(control_resolution.get("resolution") or {})
    decision_log_ref = str(resolution.get("decision_log_ref", "")).strip()
    decision_log_payload = _read_decision_log_payload(repo_root=repo_root, decision_log_ref=decision_log_ref)
    ui_messages = _decision_log_ui_messages(decision_log_payload)
    if str(control_resolution.get("result", "")) != "complete":
        refusal_payload = dict(control_resolution.get("refusal") or {})
        out = {
            "result": "refused",
            "refusal": refusal_payload,
            "resolution": dict(resolution),
            "control_intent": dict(control_intent),
            "errors": [
                {
                    "code": str(refusal_payload.get("reason_code", "refusal.ctrl.forbidden_by_law")),
                    "message": str(refusal_payload.get("message", "control resolution refused")),
                    "path": str(refusal_payload.get("path", "$")),
                }
            ],
        }
        if ui_messages:
            out["ui_messages"] = ui_messages
        return out
    emitted_intents = [
        dict(row)
        for row in list(resolution.get("emitted_intents") or [])
        if isinstance(row, dict)
    ]
    emitted_envelopes = [
        dict(row)
        for row in list(resolution.get("emitted_intent_envelopes") or [])
        if isinstance(row, dict)
    ]
    if not emitted_intents:
        out = {
            "result": "complete",
            "control_intent": control_intent,
            "resolution": resolution,
            "multiplayer_policy_id": policy_id,
        }
        if ui_messages:
            out["ui_messages"] = ui_messages
        return out
    intent = dict(emitted_intents[0])
    envelope = dict(emitted_envelopes[0]) if emitted_envelopes else {}

    from tools.xstack.sessionx.process_runtime import execute_intent as runtime_execute_intent

    execution = runtime_execute_intent(
        state=state,
        intent={
            "intent_id": str(intent.get("intent_id", "")),
            "process_id": str(intent.get("process_id", "")),
            "inputs": dict(intent.get("inputs") or {}),
        },
        law_profile=dict(law_profile or {}),
        authority_context=dict(authority_context or {}),
        navigation_indices=navigation_indices,
        policy_context=policy_context,
    )
    debug_assert_after_execute(
        state=state,
        intent={
            "intent_id": str(intent.get("intent_id", "")),
            "process_id": str(intent.get("process_id", "")),
            "inputs": dict(intent.get("inputs") or {}),
        },
        result=dict(execution or {}),
    )
    if str(execution.get("result", "")) != "complete":
        refusal_payload = dict((dict(execution or {})).get("refusal") or {})
        reason_code = str(refusal_payload.get("reason_code", "")).strip()
        if reason_code in {"refusal.tool.bind_required", "refusal.tool.not_found"}:
            _record_authority_violation(
                repo_root=repo_root,
                policy_context=policy_context,
                authority_context=authority_context,
                tick=int(tick),
                reason_code=reason_code,
                evidence=["tool spoof attempt detected during interaction execution"],
            )
        out = dict(execution)
        out["intent"] = intent
        out["envelope"] = envelope
        out["control_intent"] = control_intent
        out["resolution"] = resolution
        return out
    interaction_overlay_payload = {}
    if str(intent.get("process_id", "")).strip() == "process.inspect_generate_snapshot":
        overlay_result = build_inspection_overlays(
            perceived_model={
                "time_state": {"tick": int(max(0, _to_int(execution.get("tick", tick), tick)))},
                "entities": dict((dict(parameters or {})).get("entities") or {}),
                "populations": dict((dict(parameters or {})).get("populations") or {}),
                "truth_overlay": {
                    "state_hash_anchor": str(execution.get("state_hash_anchor", "")),
                },
            },
            target_semantic_id=str((dict(affordance_row or {})).get("target_semantic_id", "")).strip(),
            authority_context=dict(authority_context or {}),
            inspection_snapshot=dict(execution.get("inspection_snapshot") or {}),
            overlay_runtime=dict(policy_context or {}),
            requested_cost_units=int(max(1, _to_int(execution.get("inspection_cost_units", 1), 1))),
        )
        if str(overlay_result.get("result", "")) == "complete":
            interaction_overlay_payload = dict(overlay_result.get("inspection_overlays") or {})
    out = {
        "result": "complete",
        "intent": intent,
        "envelope": envelope,
        "control_intent": control_intent,
        "resolution": resolution,
        "execution": dict(execution),
        "multiplayer_policy_id": policy_id,
    }
    if ui_messages:
        out["ui_messages"] = ui_messages
    if interaction_overlay_payload:
        out["inspection_overlays"] = interaction_overlay_payload
        out["perceived_interaction_patch"] = {"inspection_overlays": interaction_overlay_payload}
    return out


def run_interaction_command(
    *,
    command: str,
    perceived_model: dict,
    law_profile: dict,
    authority_context: dict,
    interaction_action_registry: dict,
    target_semantic_id: str = "",
    affordance_id: str = "",
    parameters: dict | None = None,
    state: dict | None = None,
    navigation_indices: dict | None = None,
    policy_context: dict | None = None,
    peer_id: str = "",
    deterministic_sequence_number: int = 0,
    submission_tick: int = 0,
    source_shard_id: str = "shard.0",
    target_shard_id: str = "shard.0",
    include_disabled: bool = True,
    repo_root: str = "",
) -> Dict[str, object]:
    token = str(command).strip()
    if token == "interact.select_target":
        selected = select_target(
            perceived_model=perceived_model,
            target_semantic_id=target_semantic_id,
        )
        if str(selected.get("result", "")) != "complete":
            return selected
        selected["selection_overlay"] = build_selection_overlay(str(selected.get("target_semantic_id", "")))
        return selected
    if token == "interact.list_affordances":
        listed = build_affordance_list(
            perceived_model=perceived_model,
            target_semantic_id=target_semantic_id,
            law_profile=law_profile,
            authority_context=authority_context,
            interaction_action_registry=interaction_action_registry,
            surface_type_registry=_registry_payload(policy_context, "surface_type_registry"),
            tool_tag_registry=_registry_payload(policy_context, "tool_tag_registry"),
            tool_type_registry=_registry_payload(policy_context, "tool_type_registry"),
            tool_effect_model_registry=_registry_payload(policy_context, "tool_effect_model_registry"),
            surface_visibility_policy_registry=_registry_payload(policy_context, "surface_visibility_policy_registry"),
            held_tool_tags=_held_tool_tags(policy_context),
            active_tool=_active_tool_context(state=state, authority_context=authority_context, policy_context=policy_context),
            include_disabled=bool(include_disabled),
            repo_root=repo_root,
        )
        if str(listed.get("result", "")) != "complete":
            return listed
        listed_payload = dict(listed.get("affordance_list") or {})
        action_surfaces = list((dict(listed_payload.get("extensions") or {})).get("action_surfaces") or [])
        listed["interaction_panel"] = build_interaction_panel(
            affordance_list=listed_payload,
            selected_affordance_id="",
        )
        listed["selection_overlay"] = build_selection_overlay(
            str(target_semantic_id or ""),
            action_surfaces=action_surfaces,
        )
        return listed
    if token == "interact.preview":
        affordances = build_affordance_list(
            perceived_model=perceived_model,
            target_semantic_id=target_semantic_id,
            law_profile=law_profile,
            authority_context=authority_context,
            interaction_action_registry=interaction_action_registry,
            surface_type_registry=_registry_payload(policy_context, "surface_type_registry"),
            tool_tag_registry=_registry_payload(policy_context, "tool_tag_registry"),
            tool_type_registry=_registry_payload(policy_context, "tool_type_registry"),
            tool_effect_model_registry=_registry_payload(policy_context, "tool_effect_model_registry"),
            surface_visibility_policy_registry=_registry_payload(policy_context, "surface_visibility_policy_registry"),
            held_tool_tags=_held_tool_tags(policy_context),
            active_tool=_active_tool_context(state=state, authority_context=authority_context, policy_context=policy_context),
            include_disabled=bool(include_disabled),
            repo_root=repo_root,
        )
        affordance_list_payload = dict(affordances.get("affordance_list") or {})
        affordance_row = _find_affordance(affordance_list_payload, affordance_id=str(affordance_id or ""))
        if not affordance_row:
            return _refusal(
                "refusal.interaction.affordance_unknown",
                "preview requires valid affordance_id from current affordance list",
                "Call interact.list_affordances then retry with one returned affordance_id.",
                {"affordance_id": str(affordance_id or "")},
                "$.affordance_id",
            )
        if not bool(dict(affordance_row.get("extensions") or {}).get("enabled", False)):
            return _refusal(
                "refusal.interaction.affordance_disabled",
                "preview is unavailable for disabled affordance under current law/authority context",
                "Grant required entitlements/channels or choose another affordance.",
                {"affordance_id": str(affordance_id or "")},
                "$.affordance_id",
            )
        return generate_interaction_preview(
            perceived_model=perceived_model,
            affordance_row=affordance_row,
            parameters=dict(parameters or {}),
            preview_runtime=dict(policy_context or {}),
            repo_root=repo_root,
        )
    if token == "interact.execute":
        executed = execute_affordance(
            state=dict(state or {}),
            affordance_list=dict(
                (
                    build_affordance_list(
                        perceived_model=perceived_model,
                        target_semantic_id=target_semantic_id,
                        law_profile=law_profile,
                        authority_context=authority_context,
                        interaction_action_registry=interaction_action_registry,
                        surface_type_registry=_registry_payload(policy_context, "surface_type_registry"),
                        tool_tag_registry=_registry_payload(policy_context, "tool_tag_registry"),
                        tool_type_registry=_registry_payload(policy_context, "tool_type_registry"),
                        tool_effect_model_registry=_registry_payload(policy_context, "tool_effect_model_registry"),
                        surface_visibility_policy_registry=_registry_payload(policy_context, "surface_visibility_policy_registry"),
                        held_tool_tags=_held_tool_tags(policy_context),
                        active_tool=_active_tool_context(state=state, authority_context=authority_context, policy_context=policy_context),
                        include_disabled=bool(include_disabled),
                        repo_root=repo_root,
                    )
                ).get("affordance_list")
                or {}
            ),
            affordance_id=affordance_id,
            parameters=dict(parameters or {}),
            law_profile=dict(law_profile or {}),
            authority_context=dict(authority_context or {}),
            navigation_indices=navigation_indices,
            policy_context=policy_context,
            peer_id=peer_id,
            deterministic_sequence_number=int(deterministic_sequence_number),
            submission_tick=int(submission_tick),
            source_shard_id=str(source_shard_id or "shard.0"),
            target_shard_id=str(target_shard_id or "shard.0"),
            repo_root=repo_root,
        )
        if str(executed.get("result", "")) != "complete":
            return executed
        affordances = build_affordance_list(
            perceived_model=perceived_model,
            target_semantic_id=target_semantic_id,
            law_profile=law_profile,
            authority_context=authority_context,
            interaction_action_registry=interaction_action_registry,
            surface_type_registry=_registry_payload(policy_context, "surface_type_registry"),
            tool_tag_registry=_registry_payload(policy_context, "tool_tag_registry"),
            tool_type_registry=_registry_payload(policy_context, "tool_type_registry"),
            tool_effect_model_registry=_registry_payload(policy_context, "tool_effect_model_registry"),
            surface_visibility_policy_registry=_registry_payload(policy_context, "surface_visibility_policy_registry"),
            held_tool_tags=_held_tool_tags(policy_context),
            active_tool=_active_tool_context(state=state, authority_context=authority_context, policy_context=policy_context),
            include_disabled=bool(include_disabled),
            repo_root=repo_root,
        )
        affordance_list_payload = dict(affordances.get("affordance_list") or {})
        if affordance_list_payload:
            executed["interaction_panel"] = build_interaction_panel(
                affordance_list=affordance_list_payload,
                selected_affordance_id=str(affordance_id or ""),
            )
            action_surfaces = list((dict(affordance_list_payload.get("extensions") or {})).get("action_surfaces") or [])
        else:
            action_surfaces = []
        if "inspection_overlays" not in executed:
            executed["selection_overlay"] = build_selection_overlay(
                str(target_semantic_id or ""),
                action_surfaces=action_surfaces,
            )
        return executed
    return _refusal(
        "refusal.interaction.command_unknown",
        "unknown interaction command '{}'; supported commands are interact.select_target, interact.list_affordances, interact.preview, interact.execute".format(
            token
        ),
        "Use one of the canonical interaction command ids.",
        {"command": token},
        "$.command",
    )
