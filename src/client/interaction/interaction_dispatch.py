"""Deterministic interaction dispatch via intent envelopes and process execution."""

from __future__ import annotations

from typing import Dict, List

from src.net.anti_cheat.anti_cheat_engine import (
    check_authority_integrity,
    check_input_integrity,
)
from src.net.policies.policy_lockstep import POLICY_ID_LOCKSTEP
from src.net.policies.policy_server_authoritative import POLICY_ID_SERVER_AUTHORITATIVE
from src.net.policies.policy_srz_hybrid import POLICY_ID_SRZ_HYBRID
from tools.xstack.compatx.canonical_json import canonical_sha256

from .affordance_generator import build_affordance_list
from .inspection_overlays import build_inspection_overlays
from .interaction_panel import build_interaction_panel, build_selection_overlay
from .preview_generator import generate_interaction_preview


_DEFAULT_INTERACTION_MAX_PER_TICK = 24


def _sorted_unique_strings(values: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in (values or []) if str(item).strip()))


def _registry_payload(policy_context: dict | None, key: str) -> dict:
    return dict((dict(policy_context or {})).get(str(key), {}) or {})


def _held_tool_tags(policy_context: dict | None) -> List[object]:
    return list((dict(policy_context or {})).get("held_tool_tags") or [])


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


def build_interaction_intent(
    *,
    affordance_row: dict,
    parameters: dict,
    authority_context: dict,
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
    intent_id = "intent.interact.{}".format(
        canonical_sha256(
            {
                "affordance_id": affordance_id,
                "process_id": process_id,
                "tick": int(max(0, _to_int(tick, 0))),
                "parameters": canonical_parameters,
            }
        )[:16]
    )
    intent = {
        "intent_id": intent_id,
        "process_id": process_id,
        "inputs": canonical_parameters,
        "authority_context_ref": {
            "authority_origin": str((dict(authority_context or {})).get("authority_origin", "")),
            "law_profile_id": str((dict(authority_context or {})).get("law_profile_id", "")),
        },
        "extensions": {
            "affordance_id": affordance_id,
            "target_semantic_id": str((dict(affordance_row or {})).get("target_semantic_id", "")).strip(),
        },
    }
    return {
        "result": "complete",
        "intent": intent,
    }


def build_interaction_envelope(
    *,
    peer_id: str,
    intent: dict,
    authority_context: dict,
    pack_lock_hash: str,
    registry_hashes: dict | None,
    submission_tick: int,
    deterministic_sequence_number: int,
    source_shard_id: str = "shard.0",
    target_shard_id: str = "shard.0",
) -> Dict[str, object]:
    peer_token = str(peer_id).strip() or str((dict(authority_context or {})).get("peer_id", "")).strip() or "peer.local"
    tick = int(max(0, _to_int(submission_tick, 0)))
    sequence = int(max(0, _to_int(deterministic_sequence_number, 0)))
    intent_id = str((dict(intent or {})).get("intent_id", "")).strip()
    envelope = {
        "schema_version": "1.0.0",
        "envelope_id": "env.{}.tick.{}.seq.{}".format(peer_token, tick, str(sequence).zfill(4)),
        "authority_summary": {
            "authority_origin": str((dict(authority_context or {})).get("authority_origin", "client")),
            "law_profile_id": str((dict(authority_context or {})).get("law_profile_id", "")),
        },
        "source_peer_id": peer_token,
        "source_shard_id": str(source_shard_id or "shard.0"),
        "target_shard_id": str(target_shard_id or "shard.0"),
        "submission_tick": tick,
        "deterministic_sequence_number": sequence,
        "intent_id": intent_id,
        "payload_schema_id": "dominium.intent.process.v1",
        "payload": {
            "process_id": str((dict(intent or {})).get("process_id", "")),
            "inputs": _canonical_parameters(dict((dict(intent or {})).get("inputs") or {})),
        },
        "pack_lock_hash": _hash64(pack_lock_hash, {"peer_id": peer_token}),
        "registry_hashes": dict((dict(registry_hashes or {}))),
        "signature": "",
        "extensions": {
            "interaction_dispatch": True,
            "authority_origin": str((dict(authority_context or {})).get("authority_origin", "")),
        },
    }
    return {
        "result": "complete",
        "envelope": envelope,
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
    built_intent = build_interaction_intent(
        affordance_row=affordance_row,
        parameters=dict(parameters or {}),
        authority_context=dict(authority_context or {}),
        tick=tick,
    )
    if str(built_intent.get("result", "")) != "complete":
        return built_intent
    intent = dict(built_intent.get("intent") or {})

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

    built_envelope = build_interaction_envelope(
        peer_id=str(peer_id),
        intent=intent,
        authority_context=dict(authority_context or {}),
        pack_lock_hash=str((dict(policy_context or {})).get("pack_lock_hash", "")),
        registry_hashes=dict((dict(policy_context or {})).get("registry_hashes") or {}),
        deterministic_sequence_number=int(max(0, _to_int(deterministic_sequence_number, 0))),
        submission_tick=_policy_submission_tick(
            policy_context=policy_context,
            current_tick=int(tick),
            requested_submission_tick=int(max(0, _to_int(submission_tick, tick))),
        ),
        source_shard_id=source_shard,
        target_shard_id=target_shard,
    )
    if str(built_envelope.get("result", "")) != "complete":
        return built_envelope
    envelope = dict(built_envelope.get("envelope") or {})

    from tools.xstack.sessionx.process_runtime import execute_intent

    execution = execute_intent(
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
    if str(execution.get("result", "")) != "complete":
        out = dict(execution)
        out["intent"] = intent
        out["envelope"] = envelope
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
        "execution": dict(execution),
        "multiplayer_policy_id": policy_id,
    }
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
            surface_visibility_policy_registry=_registry_payload(policy_context, "surface_visibility_policy_registry"),
            held_tool_tags=_held_tool_tags(policy_context),
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
            surface_visibility_policy_registry=_registry_payload(policy_context, "surface_visibility_policy_registry"),
            held_tool_tags=_held_tool_tags(policy_context),
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
                        surface_visibility_policy_registry=_registry_payload(policy_context, "surface_visibility_policy_registry"),
                        held_tool_tags=_held_tool_tags(policy_context),
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
            surface_visibility_policy_registry=_registry_payload(policy_context, "surface_visibility_policy_registry"),
            held_tool_tags=_held_tool_tags(policy_context),
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
