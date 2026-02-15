"""Deterministic anti-cheat engine and module checks for multiplayer policies."""

from __future__ import annotations

import os
from typing import Dict, Iterable, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.sessionx.common import norm, write_canonical_json


ACTION_AUDIT = "audit"
ACTION_REFUSE = "refuse"
ACTION_TERMINATE = "terminate"
ACTION_THROTTLE = "throttle"
ACTION_REQUIRE_ATTESTATION = "require_attestation"

VALID_ACTIONS = (
    ACTION_AUDIT,
    ACTION_REFUSE,
    ACTION_TERMINATE,
    ACTION_THROTTLE,
    ACTION_REQUIRE_ATTESTATION,
)

POLICY_ID_DETECT_ONLY = "policy.ac.detect_only"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_tokens(items: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(items or []) if str(item).strip()))


def _runtime_server(runtime: dict) -> dict:
    payload = runtime.get("server")
    if isinstance(payload, dict):
        return payload
    payload = {}
    runtime["server"] = payload
    return payload


def _module_registry_map(runtime: dict) -> dict:
    anti = dict(runtime.get("anti_cheat") or {})
    payload = anti.get("module_registry_map")
    if isinstance(payload, dict):
        return dict(payload)
    return {}


def _policy_extensions(runtime: dict) -> dict:
    anti = dict(runtime.get("anti_cheat") or {})
    payload = anti.get("extensions")
    if isinstance(payload, dict):
        return dict(payload)
    return {}


def _policy_id(runtime: dict) -> str:
    anti = dict(runtime.get("anti_cheat") or {})
    return str(anti.get("policy_id", "")).strip()


def _clean_action(token: str, fallback: str) -> str:
    candidate = str(token).strip()
    if candidate in VALID_ACTIONS:
        return candidate
    return str(fallback).strip() if str(fallback).strip() in VALID_ACTIONS else ACTION_AUDIT


def _action_sort_key(row: dict) -> Tuple[int, str, str, str, str]:
    return (
        _as_int(row.get("tick", 0), 0),
        str(row.get("peer_id", "")),
        str(row.get("module_id", "")),
        str(row.get("action", "")),
        str(row.get("action_id", "")),
    )


def _event_sort_key(row: dict) -> Tuple[int, str, str, str]:
    return (
        _as_int(row.get("tick", 0), 0),
        str(row.get("peer_id", "")),
        str(row.get("module_id", "")),
        str(row.get("event_id", "")),
    )


def _refusal_injection_sort_key(row: dict) -> Tuple[int, str, str, str, str]:
    return (
        _as_int(row.get("tick", 0), 0),
        str(row.get("peer_id", "")),
        str(row.get("module_id", "")),
        str(row.get("reason_code", "")),
        str(row.get("action", "")),
    )


def _anchor_mismatch_sort_key(row: dict) -> Tuple[int, str, str, str]:
    return (
        _as_int(row.get("tick", 0), 0),
        str(row.get("peer_id", "")),
        str(row.get("expected_hash", "")),
        str(row.get("actual_hash", "")),
    )


def ensure_runtime_channels(runtime: dict) -> None:
    """Ensure anti-cheat run-meta channels exist on runtime.server."""

    server = _runtime_server(runtime)
    if not isinstance(server.get("anti_cheat_events"), list):
        server["anti_cheat_events"] = []
    if not isinstance(server.get("anti_cheat_enforcement_actions"), list):
        server["anti_cheat_enforcement_actions"] = []
    if not isinstance(server.get("anti_cheat_refusal_injections"), list):
        server["anti_cheat_refusal_injections"] = []
    if not isinstance(server.get("anti_cheat_anchor_mismatches"), list):
        server["anti_cheat_anchor_mismatches"] = []
    counters = server.get("anti_cheat_violation_counters")
    if not isinstance(counters, dict):
        server["anti_cheat_violation_counters"] = {}
    terminated = server.get("terminated_peers")
    if not isinstance(terminated, list):
        server["terminated_peers"] = []
    runtime["server"] = server


def module_enabled(runtime: dict, module_id: str) -> bool:
    anti = dict(runtime.get("anti_cheat") or {})
    module_ids = _sorted_tokens(list(anti.get("modules_enabled") or []))
    return str(module_id).strip() in module_ids


def default_action(runtime: dict, module_id: str, fallback: str = ACTION_AUDIT) -> str:
    anti = dict(runtime.get("anti_cheat") or {})
    defaults = anti.get("default_actions")
    if isinstance(defaults, dict):
        token = _clean_action(str(defaults.get(str(module_id), "")).strip(), fallback=str(fallback))
        if token:
            return token
    return _clean_action(str(fallback), ACTION_AUDIT)


def _counter_key(peer_id: str, module_id: str, reason_code: str) -> str:
    return "{}|{}|{}".format(str(peer_id), str(module_id), str(reason_code))


def _next_violation_count(runtime: dict, peer_id: str, module_id: str, reason_code: str) -> int:
    ensure_runtime_channels(runtime)
    server = _runtime_server(runtime)
    counters = dict(server.get("anti_cheat_violation_counters") or {})
    key = _counter_key(peer_id=peer_id, module_id=module_id, reason_code=reason_code)
    current = _as_int(counters.get(key, 0), 0)
    updated = current + 1
    counters[key] = int(updated)
    server["anti_cheat_violation_counters"] = dict((name, _as_int(value, 0)) for name, value in sorted(counters.items()))
    runtime["server"] = server
    return int(updated)


def _escalated_action(
    runtime: dict,
    module_id: str,
    reason_code: str,
    violation_count: int,
    fallback: str,
) -> str:
    policy_id = _policy_id(runtime)
    if policy_id == POLICY_ID_DETECT_ONLY:
        return ACTION_AUDIT

    base_action = _clean_action(default_action(runtime, module_id=module_id, fallback=fallback), fallback)
    extensions = _policy_extensions(runtime)
    rules_root = extensions.get("escalation_rules")
    if not isinstance(rules_root, dict):
        return base_action
    module_rules = rules_root.get(str(module_id))
    if not isinstance(module_rules, list):
        return base_action

    chosen = base_action
    rule_rows = sorted(
        (dict(row) for row in module_rules if isinstance(row, dict)),
        key=lambda row: (
            _as_int(row.get("min_count", 0), 0),
            str(row.get("reason_code", "")),
            str(row.get("action", "")),
        ),
    )
    for row in rule_rows:
        min_count = max(1, _as_int(row.get("min_count", 1), 1))
        target_reason = str(row.get("reason_code", "")).strip()
        action_token = _clean_action(str(row.get("action", "")).strip(), chosen)
        if target_reason and target_reason != str(reason_code):
            continue
        if int(violation_count) >= int(min_count):
            chosen = action_token
    return chosen


def _event_id(peer_id: str, tick: int, event_index: int) -> str:
    peer_token = str(peer_id).replace("\\", ".").replace("/", ".").replace(" ", "_")
    return "ac.{}.tick.{}.seq.{}".format(peer_token, int(tick), str(event_index).zfill(4))


def _action_id(peer_id: str, tick: int, action_index: int) -> str:
    peer_token = str(peer_id).replace("\\", ".").replace("/", ".").replace(" ", "_")
    return "ac.action.{}.tick.{}.seq.{}".format(peer_token, int(tick), str(action_index).zfill(4))


def refusal_reason_from_action(action: str, fallback_reason_code: str) -> str:
    token = str(action).strip()
    if token == ACTION_REQUIRE_ATTESTATION:
        return "refusal.ac.attestation_missing"
    if token == ACTION_TERMINATE:
        return "refusal.ac.policy_violation"
    return str(fallback_reason_code).strip()


def action_blocks_submission(action: str) -> bool:
    token = str(action).strip()
    return token in (ACTION_REFUSE, ACTION_TERMINATE, ACTION_REQUIRE_ATTESTATION)


def action_drops_without_refusal(action: str) -> bool:
    token = str(action).strip()
    return token in (ACTION_AUDIT, ACTION_THROTTLE)


def record_anchor_mismatch(
    runtime: dict,
    tick: int,
    peer_id: str,
    expected_hash: str,
    actual_hash: str,
    module_id: str = "ac.module.state_integrity",
) -> None:
    ensure_runtime_channels(runtime)
    server = _runtime_server(runtime)
    rows = list(server.get("anti_cheat_anchor_mismatches") or [])
    rows.append(
        {
            "tick": int(tick),
            "peer_id": str(peer_id),
            "module_id": str(module_id),
            "expected_hash": str(expected_hash),
            "actual_hash": str(actual_hash),
        }
    )
    server["anti_cheat_anchor_mismatches"] = sorted(
        (dict(row) for row in rows if isinstance(row, dict)),
        key=_anchor_mismatch_sort_key,
    )
    runtime["server"] = server


def _record_refusal_injection(
    runtime: dict,
    tick: int,
    peer_id: str,
    module_id: str,
    reason_code: str,
    action: str,
    event_id: str,
) -> None:
    ensure_runtime_channels(runtime)
    server = _runtime_server(runtime)
    rows = list(server.get("anti_cheat_refusal_injections") or [])
    rows.append(
        {
            "tick": int(tick),
            "peer_id": str(peer_id),
            "module_id": str(module_id),
            "reason_code": str(reason_code),
            "action": str(action),
            "event_id": str(event_id),
            "policy_id": _policy_id(runtime),
        }
    )
    server["anti_cheat_refusal_injections"] = sorted(
        (dict(row) for row in rows if isinstance(row, dict)),
        key=_refusal_injection_sort_key,
    )
    if str(action) == ACTION_TERMINATE:
        terminated = _sorted_tokens(list(server.get("terminated_peers") or []) + [str(peer_id)])
        server["terminated_peers"] = terminated
    runtime["server"] = server


def emit_event(
    repo_root: str,
    runtime: dict,
    tick: int,
    peer_id: str,
    module_id: str,
    severity: str,
    reason_code: str,
    evidence: List[str],
    default_action_token: str = ACTION_AUDIT,
    context: dict | None = None,
) -> Dict[str, object]:
    """Emit deterministic anti-cheat event and mapped enforcement action."""

    if not module_enabled(runtime, module_id):
        return {"result": "ignored", "action": ACTION_AUDIT}

    ensure_runtime_channels(runtime)
    server = _runtime_server(runtime)
    rows = list(server.get("anti_cheat_events") or [])
    event_index = len(rows) + 1
    bounded_evidence = [str(item)[:240] for item in list(evidence or []) if str(item).strip()]
    violation_count = _next_violation_count(runtime, peer_id=str(peer_id), module_id=str(module_id), reason_code=str(reason_code))
    action = _escalated_action(
        runtime=runtime,
        module_id=str(module_id),
        reason_code=str(reason_code),
        violation_count=int(violation_count),
        fallback=str(default_action_token),
    )

    fingerprint_payload = {
        "tick": int(tick),
        "peer_id": str(peer_id),
        "module_id": str(module_id),
        "severity": str(severity),
        "reason_code": str(reason_code),
        "evidence": bounded_evidence,
        "recommended_action": str(action),
        "violation_count": int(violation_count),
    }
    if isinstance(context, dict) and context:
        fingerprint_payload["context"] = dict((key, context[key]) for key in sorted(context.keys()))

    event = {
        "schema_version": "1.0.0",
        "event_id": _event_id(peer_id=str(peer_id), tick=int(tick), event_index=int(event_index)),
        "tick": int(tick),
        "peer_id": str(peer_id),
        "module_id": str(module_id),
        "severity": str(severity),
        "reason_code": str(reason_code),
        "evidence": bounded_evidence,
        "recommended_action": str(action),
        "deterministic_fingerprint": canonical_sha256(fingerprint_payload),
        "extensions": {
            "policy_id": _policy_id(runtime),
            "violation_count": int(violation_count),
            "module_declared": bool(str(module_id) in _module_registry_map(runtime)),
        },
    }
    if isinstance(context, dict) and context:
        event_extensions = dict(event.get("extensions") or {})
        event_extensions["context"] = dict((key, context[key]) for key in sorted(context.keys()))
        event["extensions"] = event_extensions

    checked = validate_instance(
        repo_root=repo_root,
        schema_name="net_anti_cheat_event",
        payload=event,
        strict_top_level=True,
    )
    if not bool(checked.get("valid", False)):
        return {"result": "refused", "action": ACTION_AUDIT}

    rows.append(event)
    server["anti_cheat_events"] = sorted(
        (dict(row) for row in rows if isinstance(row, dict)),
        key=_event_sort_key,
    )

    action_rows = list(server.get("anti_cheat_enforcement_actions") or [])
    action_index = len(action_rows) + 1
    action_payload = {
        "action_id": _action_id(peer_id=str(peer_id), tick=int(tick), action_index=int(action_index)),
        "tick": int(tick),
        "peer_id": str(peer_id),
        "module_id": str(module_id),
        "reason_code": str(reason_code),
        "action": str(action),
        "event_id": str(event.get("event_id", "")),
        "policy_id": _policy_id(runtime),
        "deterministic_fingerprint": canonical_sha256(
            {
                "tick": int(tick),
                "peer_id": str(peer_id),
                "module_id": str(module_id),
                "reason_code": str(reason_code),
                "action": str(action),
                "event_id": str(event.get("event_id", "")),
                "policy_id": _policy_id(runtime),
            }
        ),
        "extensions": {},
    }
    action_rows.append(action_payload)
    server["anti_cheat_enforcement_actions"] = sorted(
        (dict(row) for row in action_rows if isinstance(row, dict)),
        key=_action_sort_key,
    )
    runtime["server"] = server

    if action_blocks_submission(action):
        _record_refusal_injection(
            runtime=runtime,
            tick=int(tick),
            peer_id=str(peer_id),
            module_id=str(module_id),
            reason_code=refusal_reason_from_action(action, fallback_reason_code=str(reason_code)),
            action=str(action),
            event_id=str(event.get("event_id", "")),
        )

    return {
        "result": "complete",
        "event": event,
        "action": str(action),
        "violation_count": int(violation_count),
    }


def check_sequence_integrity(
    repo_root: str,
    runtime: dict,
    tick: int,
    peer_id: str,
    sequence: int,
    expected_sequence: int,
    default_action_token: str = ACTION_REFUSE,
) -> Dict[str, object]:
    if int(sequence) == int(expected_sequence):
        return {"result": "complete", "action": ACTION_AUDIT}
    event_result = emit_event(
        repo_root=repo_root,
        runtime=runtime,
        tick=int(tick),
        peer_id=str(peer_id),
        module_id="ac.module.sequence_integrity",
        severity="violation",
        reason_code="refusal.net.sequence_violation",
        evidence=[
            "deterministic_sequence_number is out of order",
            "expected={},actual={}".format(int(expected_sequence), int(sequence)),
        ],
        default_action_token=str(default_action_token),
    )
    return {
        "result": "violation",
        "action": str(event_result.get("action", ACTION_AUDIT)),
        "event": dict(event_result.get("event") or {}),
        "reason_code": "refusal.net.sequence_violation",
    }


def check_replay_protection(
    repo_root: str,
    runtime: dict,
    tick: int,
    peer_id: str,
    envelope_id: str,
    seen_envelope_ids: List[str],
    default_action_token: str = ACTION_REFUSE,
) -> Dict[str, object]:
    if str(envelope_id).strip() not in set(_sorted_tokens(list(seen_envelope_ids or []))):
        return {"result": "complete", "action": ACTION_AUDIT}
    event_result = emit_event(
        repo_root=repo_root,
        runtime=runtime,
        tick=int(tick),
        peer_id=str(peer_id),
        module_id="ac.module.replay_protection",
        severity="violation",
        reason_code="refusal.net.replay_detected",
        evidence=["duplicate envelope_id detected", "envelope_id={}".format(str(envelope_id))],
        default_action_token=str(default_action_token),
    )
    return {
        "result": "violation",
        "action": str(event_result.get("action", ACTION_AUDIT)),
        "event": dict(event_result.get("event") or {}),
        "reason_code": "refusal.net.replay_detected",
    }


def check_authority_integrity(
    repo_root: str,
    runtime: dict,
    tick: int,
    peer_id: str,
    allowed: bool,
    reason_code: str,
    evidence: List[str],
    default_action_token: str = ACTION_REFUSE,
) -> Dict[str, object]:
    if bool(allowed):
        return {"result": "complete", "action": ACTION_AUDIT}
    event_result = emit_event(
        repo_root=repo_root,
        runtime=runtime,
        tick=int(tick),
        peer_id=str(peer_id),
        module_id="ac.module.authority_integrity",
        severity="violation",
        reason_code=str(reason_code),
        evidence=list(evidence or []),
        default_action_token=str(default_action_token),
    )
    return {
        "result": "violation",
        "action": str(event_result.get("action", ACTION_AUDIT)),
        "event": dict(event_result.get("event") or {}),
        "reason_code": str(reason_code),
    }


def check_input_integrity(
    repo_root: str,
    runtime: dict,
    tick: int,
    peer_id: str,
    valid: bool,
    reason_code: str,
    evidence: List[str],
    default_action_token: str = ACTION_REFUSE,
) -> Dict[str, object]:
    if bool(valid):
        return {"result": "complete", "action": ACTION_AUDIT}
    event_result = emit_event(
        repo_root=repo_root,
        runtime=runtime,
        tick=int(tick),
        peer_id=str(peer_id),
        module_id="ac.module.input_integrity",
        severity="warn",
        reason_code=str(reason_code),
        evidence=list(evidence or []),
        default_action_token=str(default_action_token),
    )
    return {
        "result": "violation",
        "action": str(event_result.get("action", ACTION_AUDIT)),
        "event": dict(event_result.get("event") or {}),
        "reason_code": str(reason_code),
    }


def check_state_integrity(
    repo_root: str,
    runtime: dict,
    tick: int,
    peer_id: str,
    expected_hash: str,
    actual_hash: str,
    reason_code: str = "refusal.net.resync_required",
    default_action_token: str = ACTION_AUDIT,
) -> Dict[str, object]:
    if str(expected_hash).strip() == str(actual_hash).strip():
        return {"result": "complete", "action": ACTION_AUDIT}
    record_anchor_mismatch(
        runtime=runtime,
        tick=int(tick),
        peer_id=str(peer_id),
        expected_hash=str(expected_hash),
        actual_hash=str(actual_hash),
    )
    event_result = emit_event(
        repo_root=repo_root,
        runtime=runtime,
        tick=int(tick),
        peer_id=str(peer_id),
        module_id="ac.module.state_integrity",
        severity="violation",
        reason_code=str(reason_code),
        evidence=[
            "hash anchor mismatch detected",
            "expected={},actual={}".format(str(expected_hash), str(actual_hash)),
        ],
        default_action_token=str(default_action_token),
    )
    return {
        "result": "violation",
        "action": str(event_result.get("action", ACTION_AUDIT)),
        "event": dict(event_result.get("event") or {}),
        "reason_code": str(reason_code),
    }


def check_behavioral_detection(
    repo_root: str,
    runtime: dict,
    tick: int,
    peer_id: str,
    suspicious: bool,
    reason_code: str = "ac.behavior.pattern_suspect",
    evidence: List[str] | None = None,
    default_action_token: str = ACTION_AUDIT,
) -> Dict[str, object]:
    if not bool(suspicious):
        return {"result": "complete", "action": ACTION_AUDIT}
    event_result = emit_event(
        repo_root=repo_root,
        runtime=runtime,
        tick=int(tick),
        peer_id=str(peer_id),
        module_id="ac.module.behavioral_detection",
        severity="warn",
        reason_code=str(reason_code),
        evidence=list(evidence or ["behavioral heuristic threshold reached"]),
        default_action_token=str(default_action_token),
    )
    return {
        "result": "violation",
        "action": str(event_result.get("action", ACTION_AUDIT)),
        "event": dict(event_result.get("event") or {}),
        "reason_code": str(reason_code),
    }


def check_client_attestation(
    repo_root: str,
    runtime: dict,
    tick: int,
    peer_id: str,
    required: bool,
    attestation_token: str,
    default_action_token: str = ACTION_REQUIRE_ATTESTATION,
) -> Dict[str, object]:
    if not bool(required):
        return {"result": "complete", "action": ACTION_AUDIT}
    if str(attestation_token).strip():
        return {"result": "complete", "action": ACTION_AUDIT}
    event_result = emit_event(
        repo_root=repo_root,
        runtime=runtime,
        tick=int(tick),
        peer_id=str(peer_id),
        module_id="ac.module.client_attestation",
        severity="violation",
        reason_code="refusal.ac.attestation_missing",
        evidence=["client attestation token missing while policy requires attestation"],
        default_action_token=str(default_action_token),
    )
    return {
        "result": "violation",
        "action": str(event_result.get("action", ACTION_AUDIT)),
        "event": dict(event_result.get("event") or {}),
        "reason_code": "refusal.ac.attestation_missing",
    }


def _artifact_header(runtime: dict, artifact_type_id: str) -> dict:
    server = _runtime_server(runtime)
    lock_payload = dict(runtime.get("lock_payload") or {})
    pack_lock_hash = str(lock_payload.get("pack_lock_hash", "")) or str(server.get("pack_lock_hash", ""))
    registry_hashes = dict(server.get("registry_hashes") or {})
    compatibility_version = str(lock_payload.get("compatibility_version", "")) or str(runtime.get("compatibility_version", ""))
    return {
        "schema_version": "1.0.0",
        "artifact_type_id": str(artifact_type_id),
        "policy_id": _policy_id(runtime),
        "pack_lock_hash": str(pack_lock_hash),
        "registry_hashes": dict((key, registry_hashes[key]) for key in sorted(registry_hashes.keys())),
        "bii": str(compatibility_version),
    }


def _write_payload(repo_root: str, runtime: dict, rel_path: str, payload: dict) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    write_canonical_json(abs_path, payload)
    return norm(os.path.relpath(abs_path, repo_root))


def export_proof_artifacts(repo_root: str, runtime: dict, run_id: str = "") -> Dict[str, object]:
    """Write deterministic anti-cheat proof artifacts under runtime run_meta path."""

    ensure_runtime_channels(runtime)
    server = _runtime_server(runtime)
    run_token = str(run_id).strip() or "latest"
    artifacts_rel = str(runtime.get("artifacts_rel", "")).strip() or norm(
        os.path.join("build", "net", "anti_cheat", str(runtime.get("save_id", "save.unknown")))
    )
    output_root_rel = norm(os.path.join(artifacts_rel, "run_meta", "anti_cheat"))

    event_rows = sorted((dict(row) for row in list(server.get("anti_cheat_events") or []) if isinstance(row, dict)), key=_event_sort_key)
    action_rows = sorted(
        (dict(row) for row in list(server.get("anti_cheat_enforcement_actions") or []) if isinstance(row, dict)),
        key=_action_sort_key,
    )
    anchor_rows = sorted(
        (dict(row) for row in list(server.get("anti_cheat_anchor_mismatches") or []) if isinstance(row, dict)),
        key=_anchor_mismatch_sort_key,
    )
    refusal_rows = sorted(
        (dict(row) for row in list(server.get("anti_cheat_refusal_injections") or []) if isinstance(row, dict)),
        key=_refusal_injection_sort_key,
    )

    payloads = {
        "events": {
            **_artifact_header(runtime=runtime, artifact_type_id="anti_cheat.events"),
            "run_id": run_token,
            "rows": event_rows,
            "row_count": int(len(event_rows)),
            "extensions": {},
        },
        "actions": {
            **_artifact_header(runtime=runtime, artifact_type_id="anti_cheat.enforcement_actions"),
            "run_id": run_token,
            "rows": action_rows,
            "row_count": int(len(action_rows)),
            "extensions": {},
        },
        "anchor_mismatches": {
            **_artifact_header(runtime=runtime, artifact_type_id="anti_cheat.anchor_mismatches"),
            "run_id": run_token,
            "rows": anchor_rows,
            "row_count": int(len(anchor_rows)),
            "extensions": {},
        },
        "refusal_injections": {
            **_artifact_header(runtime=runtime, artifact_type_id="anti_cheat.refusal_injections"),
            "run_id": run_token,
            "rows": refusal_rows,
            "row_count": int(len(refusal_rows)),
            "extensions": {},
        },
    }

    artifact_paths = {}
    artifact_hashes = {}
    for key in sorted(payloads.keys()):
        file_name = "anti_cheat.{}.{}.json".format(key, run_token)
        rel_path = norm(os.path.join(output_root_rel, file_name))
        written_rel = _write_payload(repo_root=repo_root, runtime=runtime, rel_path=rel_path, payload=dict(payloads[key]))
        artifact_paths[key] = written_rel
        artifact_hashes[key] = canonical_sha256(dict(payloads[key]))

    manifest = {
        **_artifact_header(runtime=runtime, artifact_type_id="anti_cheat.proof_manifest"),
        "run_id": run_token,
        "artifact_paths": dict((key, artifact_paths[key]) for key in sorted(artifact_paths.keys())),
        "artifact_hashes": dict((key, artifact_hashes[key]) for key in sorted(artifact_hashes.keys())),
        "extensions": {},
    }
    manifest_rel = norm(os.path.join(output_root_rel, "anti_cheat.proof_manifest.{}.json".format(run_token)))
    manifest_path = _write_payload(repo_root=repo_root, runtime=runtime, rel_path=manifest_rel, payload=manifest)

    server["anti_cheat_proof_artifacts"] = {
        "run_id": run_token,
        "manifest_path": manifest_path,
        "artifact_paths": dict((key, artifact_paths[key]) for key in sorted(artifact_paths.keys())),
        "artifact_hashes": dict((key, artifact_hashes[key]) for key in sorted(artifact_hashes.keys())),
    }
    runtime["server"] = server

    return {
        "result": "complete",
        "manifest_path": manifest_path,
        "artifact_paths": dict((key, artifact_paths[key]) for key in sorted(artifact_paths.keys())),
        "artifact_hashes": dict((key, artifact_hashes[key]) for key in sorted(artifact_hashes.keys())),
    }

