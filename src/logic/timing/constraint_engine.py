"""LOGIC-5 timing constraint helpers."""

from __future__ import annotations

from typing import Mapping

from src.logic.eval.common import as_int, as_map, canon, token
from src.meta.explain import build_explain_artifact

from tools.xstack.compatx.canonical_json import canonical_sha256


def declared_timing_constraint(binding_row: Mapping[str, object] | None) -> dict:
    extensions = as_map(as_map(binding_row).get("extensions"))
    constraint = as_map(extensions.get("timing_constraint"))
    if not constraint:
        return {}
    constraint_id = token(constraint.get("constraint_id"))
    max_propagation_ticks = int(max(1, as_int(constraint.get("max_propagation_ticks", 1), 1)))
    max_cycle_ticks = constraint.get("max_cycle_ticks")
    normalized = {
        "constraint_id": constraint_id or "logic.constraint.unnamed",
        "max_propagation_ticks": int(max_propagation_ticks),
        "max_cycle_ticks": None if max_cycle_ticks is None else int(max(1, as_int(max_cycle_ticks, 1))),
        "extensions": canon(as_map(constraint.get("extensions"))),
    }
    normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
    return normalized


def evaluate_logic_timing_constraints(
    *,
    current_tick: int,
    network_id: str,
    binding_row: Mapping[str, object] | None,
    logic_policy_row: Mapping[str, object] | None,
    propagation_result: Mapping[str, object] | None,
    oscillation_classification: Mapping[str, object] | None = None,
) -> dict:
    tick = int(max(0, as_int(current_tick, 0)))
    network_token = token(network_id)
    constraint = declared_timing_constraint(binding_row)
    if not constraint:
        return {
            "constraint": {},
            "runtime_extensions": {},
            "timing_violation_events": [],
            "explain_artifact_rows": [],
        }
    policy_extensions = as_map(as_map(logic_policy_row).get("extensions"))
    max_propagation_delay_ticks = int(
        max(0, as_int(as_map(propagation_result).get("max_propagation_delay_ticks", 0), 0))
    )
    violation_rows = []
    explain_rows = []
    reasons = []
    if max_propagation_delay_ticks > int(constraint.get("max_propagation_ticks", 1)):
        reasons.append("max_propagation_ticks_exceeded")
    oscillation = as_map(oscillation_classification)
    max_cycle_ticks = constraint.get("max_cycle_ticks")
    if max_cycle_ticks is not None and oscillation:
        if int(max(1, as_int(oscillation.get("period_ticks", 1), 1))) > int(max_cycle_ticks):
            reasons.append("max_cycle_ticks_exceeded")
    for reason in reasons:
        violation_rows.append(
            {
                "tick": int(tick),
                "network_id": network_token,
                "reason": str(reason),
                "extensions": {
                    "constraint_id": token(constraint.get("constraint_id")),
                    "max_propagation_ticks": int(constraint.get("max_propagation_ticks", 1)),
                    "observed_propagation_ticks": int(max_propagation_delay_ticks),
                    "timing_violation_action": token(policy_extensions.get("timing_violation_action")) or "force_roi",
                    "oscillation_classification": canon(oscillation),
                },
            }
        )
        explain_rows.append(
            build_explain_artifact(
                explain_id="explain.logic_timing_violation.{}".format(
                    canonical_sha256(
                        {
                            "tick": int(tick),
                            "network_id": network_token,
                            "constraint_id": token(constraint.get("constraint_id")),
                            "reason": str(reason),
                        }
                    )[:16]
                ),
                event_id="event.logic.timing_violation.{}".format(
                    canonical_sha256(
                        {
                            "tick": int(tick),
                            "network_id": network_token,
                            "constraint_id": token(constraint.get("constraint_id")),
                            "reason": str(reason),
                        }
                    )[:16]
                ),
                target_id=network_token,
                cause_chain=["cause.logic.timing_constraint"],
                remediation_hints=["adjust delay policy, topology depth, or declared timing constraint"],
                extensions={
                    "event_kind_id": "explain.logic_timing_violation",
                    "constraint_id": token(constraint.get("constraint_id")),
                    "reason": str(reason),
                },
            )
        )
    return {
        "constraint": constraint,
        "runtime_extensions": {
            "timing_constraint_id": token(constraint.get("constraint_id")),
            "timing_status": "violation_detected" if reasons else "nominal",
            "max_propagation_delay_ticks": int(max_propagation_delay_ticks),
            "timing_violation_action": token(policy_extensions.get("timing_violation_action")) or "force_roi",
        },
        "timing_violation_events": violation_rows,
        "explain_artifact_rows": explain_rows,
    }


__all__ = [
    "declared_timing_constraint",
    "evaluate_logic_timing_constraints",
]
