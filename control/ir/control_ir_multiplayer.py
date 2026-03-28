"""Multiplayer safety helpers for deterministic Control IR execution."""

from __future__ import annotations

from typing import Mapping

from .control_ir_verifier import REFUSAL_CTRL_IR_INVALID


_SERVER_AUTH_POLICIES = {
    "policy.net.server_authoritative",
}
_HYBRID_POLICIES = {
    "policy.net.srz_hybrid",
}
_LOCKSTEP_POLICIES = {
    "policy.net.lockstep",
}


def _network_policy_id(policy_context: Mapping[str, object] | None) -> str:
    payload = dict(policy_context or {})
    for key in ("net_policy_id", "replication_policy_id"):
        token = str(payload.get(key, "")).strip()
        if token:
            return token
    return ""


def _is_ranked_profile(policy_context: Mapping[str, object] | None) -> bool:
    payload = dict(policy_context or {})
    token = str(payload.get("server_profile_id", "")).strip().lower()
    return "rank" in token


def multiplayer_ir_mode(policy_context: Mapping[str, object] | None) -> str:
    policy_id = _network_policy_id(policy_context)
    if policy_id in _SERVER_AUTH_POLICIES:
        return "server_authoritative"
    if policy_id in _HYBRID_POLICIES:
        return "srz_hybrid"
    if policy_id in _LOCKSTEP_POLICIES:
        return "lockstep"
    return "local"


def validate_control_ir_multiplayer(
    *,
    ir_program: Mapping[str, object],
    verification_report: Mapping[str, object],
    policy_context: Mapping[str, object] | None,
) -> dict:
    """Validate Control IR verification output for multiplayer execution modes."""

    mode = multiplayer_ir_mode(policy_context)
    if mode == "local":
        return {
            "result": "complete",
            "mode": mode,
            "requires_server_verification": False,
            "requires_decision_logging": False,
            "client_resolution_payload": "full",
            "verification_report_hash": str((dict(verification_report or {})).get("deterministic_fingerprint", "")).strip(),
        }

    report = dict(verification_report or {})
    if not bool(report.get("valid", False)):
        return {
            "result": "refused",
            "refusal": {
                "reason_code": REFUSAL_CTRL_IR_INVALID,
                "message": "multiplayer mode requires a valid Control IR verification report",
                "remediation_hint": "Fix Control IR verification violations before multiplayer execution.",
                "relevant_ids": {
                    "mode": mode,
                    "ir_id": str((dict(ir_program or {})).get("control_ir_id", "")).strip(),
                },
                "path": "$.verification_report",
            },
            "errors": [
                {
                    "code": REFUSAL_CTRL_IR_INVALID,
                    "message": "multiplayer mode requires valid Control IR verification",
                    "path": "$.verification_report",
                }
            ],
            "mode": mode,
        }

    report_hash = str(report.get("deterministic_fingerprint", "")).strip()
    if mode == "lockstep" and not report_hash:
        return {
            "result": "refused",
            "refusal": {
                "reason_code": REFUSAL_CTRL_IR_INVALID,
                "message": "lockstep mode requires verification report fingerprint",
                "remediation_hint": "Provide deterministic_fingerprint in Control IR verification report.",
                "relevant_ids": {
                    "mode": mode,
                    "ir_id": str((dict(ir_program or {})).get("control_ir_id", "")).strip(),
                },
                "path": "$.verification_report.deterministic_fingerprint",
            },
            "errors": [
                {
                    "code": REFUSAL_CTRL_IR_INVALID,
                    "message": "lockstep mode requires verification report fingerprint",
                    "path": "$.verification_report.deterministic_fingerprint",
                }
            ],
            "mode": mode,
        }

    return {
        "result": "complete",
        "mode": mode,
        "requires_server_verification": mode in ("server_authoritative", "srz_hybrid", "lockstep"),
        "requires_decision_logging": mode in ("server_authoritative", "srz_hybrid", "lockstep"),
        "client_resolution_payload": "resolved_vector_only" if mode in ("server_authoritative", "srz_hybrid", "lockstep") else "full",
        "ranked_proof_requires_decision_log_hash": bool(_is_ranked_profile(policy_context)),
        "verification_report_hash": report_hash,
    }


__all__ = [
    "multiplayer_ir_mode",
    "validate_control_ir_multiplayer",
]
