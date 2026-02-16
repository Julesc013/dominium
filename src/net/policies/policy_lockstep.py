"""Deterministic lockstep anti-cheat ingress helpers (policy.net.lockstep)."""

from __future__ import annotations

from typing import Dict

from src.net.anti_cheat import (
    check_authority_integrity,
    check_behavioral_detection,
    check_input_integrity,
    check_replay_protection,
    check_sequence_integrity,
)
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.sessionx.common import refusal


POLICY_ID_LOCKSTEP = "policy.net.lockstep"
MOVEMENT_PROCESS_IDS = ("process.agent_move", "process.agent_rotate")


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _vector3_int(payload: object) -> dict:
    row = dict(payload) if isinstance(payload, dict) else {}
    return {
        "x": _as_int(row.get("x", 0), 0),
        "y": _as_int(row.get("y", 0), 0),
        "z": _as_int(row.get("z", 0), 0),
    }


def _movement_limits(runtime: dict) -> dict:
    ext = dict((runtime.get("anti_cheat") or {}).get("extensions") or {})
    return {
        "max_intents_per_tick": max(1, _as_int(ext.get("movement_intents_per_tick_max", 3), 3)),
        "max_displacement_mm_per_tick": max(1, _as_int(ext.get("movement_max_displacement_mm_per_tick", 8000), 8000)),
    }


def _movement_requested_distance(inputs: dict) -> tuple[int, int]:
    payload = dict(inputs if isinstance(inputs, dict) else {})
    local = _vector3_int(payload.get("move_vector_local"))
    if local == {"x": 0, "y": 0, "z": 0}:
        local = _vector3_int(payload.get("delta_local_mm"))
    speed_scalar = max(0, _as_int(payload.get("speed_scalar", 1000), 1000))
    dt_ticks = max(1, _as_int(payload.get("tick_duration", payload.get("dt_ticks", 1)), 1))
    scaled = {
        "x": int(int(local["x"]) * int(speed_scalar) // 1000),
        "y": int(int(local["y"]) * int(speed_scalar) // 1000),
        "z": int(int(local["z"]) * int(speed_scalar) // 1000),
    }
    return int(abs(scaled["x"]) + abs(scaled["y"]) + abs(scaled["z"])), int(dt_ticks)


def validate_lockstep_envelope(
    repo_root: str,
    runtime: dict,
    envelope: dict,
    *,
    current_tick: int,
    lead_ticks: int,
) -> Dict[str, object]:
    """Validate lockstep envelope ingress with deterministic anti-cheat checks."""

    checked = validate_instance(
        repo_root=repo_root,
        schema_name="net_intent_envelope",
        payload=dict(envelope if isinstance(envelope, dict) else {}),
        strict_top_level=True,
    )
    if not bool(checked.get("valid", False)):
        return check_input_integrity(
            repo_root=repo_root,
            runtime=runtime,
            tick=int(max(0, current_tick)),
            peer_id=str((envelope or {}).get("source_peer_id", "peer.unknown")),
            valid=False,
            reason_code="refusal.net.envelope_invalid",
            evidence=["lockstep envelope failed schema validation"],
            default_action_token="refuse",
        )

    server = dict(runtime.get("server") or {})
    peer_id = str(envelope.get("source_peer_id", "")).strip()
    peer_rows = dict(runtime.get("clients") or {})
    if peer_id not in peer_rows:
        return check_authority_integrity(
            repo_root=repo_root,
            runtime=runtime,
            tick=int(max(0, current_tick)),
            peer_id=peer_id,
            allowed=False,
            reason_code="refusal.net.authority_violation",
            evidence=["lockstep source peer is not joined"],
            default_action_token="refuse",
        )

    submission_tick = _as_int(envelope.get("submission_tick", 0), 0)
    min_tick = int(max(0, current_tick + max(0, int(lead_ticks))))
    max_tick = int(min_tick + max(0, int(lead_ticks)))
    tick_valid = int(submission_tick) >= int(min_tick) and int(submission_tick) <= int(max_tick)
    if not tick_valid:
        return check_input_integrity(
            repo_root=repo_root,
            runtime=runtime,
            tick=int(max(0, current_tick)),
            peer_id=peer_id,
            valid=False,
            reason_code="refusal.net.envelope_invalid",
            evidence=[
                "lockstep submission_tick outside deterministic lead window",
                "submission_tick={},min_tick={},max_tick={}".format(int(submission_tick), int(min_tick), int(max_tick)),
            ],
            default_action_token="refuse",
        )

    seen = list(server.get("seen_envelope_ids") or [])
    replay = check_replay_protection(
        repo_root=repo_root,
        runtime=runtime,
        tick=int(max(0, current_tick)),
        peer_id=peer_id,
        envelope_id=str(envelope.get("envelope_id", "")),
        seen_envelope_ids=[str(item) for item in seen],
        default_action_token="refuse",
    )
    if str(replay.get("result", "")) != "complete":
        return replay

    last_seq_map = dict(server.get("last_sequence_by_peer") or {})
    expected_next = _as_int(last_seq_map.get(peer_id, 0), 0) + 1
    sequence = _as_int(envelope.get("deterministic_sequence_number", 0), 0)
    sequence_check = check_sequence_integrity(
        repo_root=repo_root,
        runtime=runtime,
        tick=int(max(0, current_tick)),
        peer_id=peer_id,
        sequence=int(sequence),
        expected_sequence=int(expected_next),
        default_action_token="refuse",
    )
    if str(sequence_check.get("result", "")) != "complete":
        return sequence_check

    payload = dict(envelope.get("payload") or {})
    process_id = str(payload.get("process_id", "")).strip()
    if process_id in MOVEMENT_PROCESS_IDS:
        limits = _movement_limits(runtime=runtime)
        movement_inputs = dict(payload.get("inputs") or {})
        submission_tick = _as_int(envelope.get("submission_tick", 0), 0)
        queued_rows = list((runtime.get("server") or {}).get("intent_queue") or [])
        movement_count = 0
        for queued in queued_rows:
            if not isinstance(queued, dict):
                continue
            if str(queued.get("source_peer_id", "")).strip() != peer_id:
                continue
            if _as_int(queued.get("submission_tick", 0), 0) != int(submission_tick):
                continue
            queued_payload = dict(queued.get("payload") or {})
            queued_process = str(queued_payload.get("process_id", "")).strip()
            if queued_process in MOVEMENT_PROCESS_IDS:
                movement_count += 1
        if int(movement_count) >= int(limits["max_intents_per_tick"]):
            return check_input_integrity(
                repo_root=repo_root,
                runtime=runtime,
                tick=int(max(0, current_tick)),
                peer_id=peer_id,
                valid=False,
                reason_code="ac.movement.intent_rate_exceeded",
                evidence=[
                    "movement intent frequency exceeded deterministic per-tick limit",
                    "submission_tick={},current_count={},max_count={}".format(
                        int(submission_tick),
                        int(movement_count),
                        int(limits["max_intents_per_tick"]),
                    ),
                ],
                default_action_token="throttle",
            )

        requested_distance_mm, requested_dt_ticks = _movement_requested_distance(movement_inputs)
        max_distance_mm = int(limits["max_displacement_mm_per_tick"]) * int(max(1, requested_dt_ticks))
        if int(requested_distance_mm) > int(max_distance_mm):
            return check_behavioral_detection(
                repo_root=repo_root,
                runtime=runtime,
                tick=int(max(0, current_tick)),
                peer_id=peer_id,
                suspicious=True,
                reason_code="ac.movement.requested_displacement_exceeded",
                evidence=[
                    "movement request exceeds deterministic displacement threshold",
                    "requested_distance_mm={},max_distance_mm={},dt_ticks={}".format(
                        int(requested_distance_mm),
                        int(max_distance_mm),
                        int(max(1, requested_dt_ticks)),
                    ),
                ],
                default_action_token="throttle",
            )

    return {"result": "complete", "action": "audit"}


def refusal_from_decision(
    decision: dict,
    *,
    peer_id: str,
    fallback_reason: str,
    message: str,
    remediation: str,
    path: str,
) -> Dict[str, object]:
    action = str(decision.get("action", "refuse"))
    if action in ("audit", "throttle"):
        return {"result": "complete", "accepted": False, "action": action}
    reason_code = str(decision.get("reason_code", "")).strip() or str(fallback_reason)
    if action == "require_attestation":
        reason_code = "refusal.ac.attestation_missing"
    if action == "terminate":
        reason_code = "refusal.ac.policy_violation"
    return refusal(
        reason_code,
        str(message),
        str(remediation),
        {"peer_id": str(peer_id)},
        str(path),
    )
