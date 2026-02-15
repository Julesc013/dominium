"""Deterministic lockstep anti-cheat ingress helpers (policy.net.lockstep)."""

from __future__ import annotations

from typing import Dict

from src.net.anti_cheat import (
    check_authority_integrity,
    check_input_integrity,
    check_replay_protection,
    check_sequence_integrity,
)
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.sessionx.common import refusal


POLICY_ID_LOCKSTEP = "policy.net.lockstep"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


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

