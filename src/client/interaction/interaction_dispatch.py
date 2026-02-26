"""Deterministic interaction dispatch via intent envelopes and process execution."""

from __future__ import annotations

from typing import Dict, List

from tools.xstack.compatx.canonical_json import canonical_sha256

from .affordance_generator import build_affordance_list


def _sorted_unique_strings(values: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in (values or []) if str(item).strip()))


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
) -> Dict[str, object]:
    affordance_row = _find_affordance(affordance_list=affordance_list, affordance_id=affordance_id)
    if not affordance_row:
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
    built_intent = build_interaction_intent(
        affordance_row=affordance_row,
        parameters=dict(parameters or {}),
        authority_context=dict(authority_context or {}),
        tick=tick,
    )
    if str(built_intent.get("result", "")) != "complete":
        return built_intent
    intent = dict(built_intent.get("intent") or {})

    built_envelope = build_interaction_envelope(
        peer_id=str(peer_id),
        intent=intent,
        authority_context=dict(authority_context or {}),
        pack_lock_hash=str((dict(policy_context or {})).get("pack_lock_hash", "")),
        registry_hashes=dict((dict(policy_context or {})).get("registry_hashes") or {}),
        deterministic_sequence_number=int(max(0, _to_int(deterministic_sequence_number, 0))),
        submission_tick=int(max(0, _to_int(submission_tick, tick))),
        source_shard_id=str(source_shard_id or "shard.0"),
        target_shard_id=str(target_shard_id or "shard.0"),
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
    return {
        "result": "complete",
        "intent": intent,
        "envelope": envelope,
        "execution": dict(execution),
    }


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
    include_disabled: bool = True,
    repo_root: str = "",
) -> Dict[str, object]:
    token = str(command).strip()
    if token == "interact.select_target":
        return select_target(
            perceived_model=perceived_model,
            target_semantic_id=target_semantic_id,
        )
    if token == "interact.list_affordances":
        return build_affordance_list(
            perceived_model=perceived_model,
            target_semantic_id=target_semantic_id,
            law_profile=law_profile,
            authority_context=authority_context,
            interaction_action_registry=interaction_action_registry,
            include_disabled=bool(include_disabled),
            repo_root=repo_root,
        )
    if token == "interact.execute":
        return execute_affordance(
            state=dict(state or {}),
            affordance_list=dict(
                (
                    build_affordance_list(
                        perceived_model=perceived_model,
                        target_semantic_id=target_semantic_id,
                        law_profile=law_profile,
                        authority_context=authority_context,
                        interaction_action_registry=interaction_action_registry,
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
        )
    return _refusal(
        "refusal.interaction.command_unknown",
        "unknown interaction command '{}'; supported commands are interact.select_target, interact.list_affordances, interact.execute".format(
            token
        ),
        "Use one of the canonical interaction command ids.",
        {"command": token},
        "$.command",
    )

