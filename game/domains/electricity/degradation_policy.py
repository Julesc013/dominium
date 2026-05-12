"""ELEC-5 deterministic degradation policy helpers."""

from __future__ import annotations

from typing import List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_ELEC_LOW_PRIORITY_CONNECTION = "refusal.elec.low_priority_connection_budget"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _with_fingerprint(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    payload["deterministic_fingerprint"] = ""
    out = dict(payload)
    out["deterministic_fingerprint"] = canonical_sha256(payload)
    return out


def apply_elec_budget_degradation(
    *,
    current_tick: int,
    budget_envelope_id: str,
    network_count: int,
    max_network_solves: int,
    e1_enabled: bool,
    pending_low_priority_connections: int,
    strict_profile_enabled: bool,
    base_model_cost_cap: int = 4096,
) -> dict:
    """Apply deterministic ELEC degradation order under budget pressure.

    Ordered policy:
    1) reduce E1 solve frequency
    2) downgrade selected networks to E0
    3) defer non-critical constitutive models
    4) refuse low-priority new connections
    """

    tick = int(max(0, _as_int(current_tick, 0)))
    envelope_id = str(budget_envelope_id or "").strip() or "elec.envelope.standard"
    networks = int(max(0, _as_int(network_count, 0)))
    solve_cap = int(max(1, _as_int(max_network_solves, 1)))
    pending_low = int(max(0, _as_int(pending_low_priority_connections, 0)))
    model_cost_cap = int(max(1, _as_int(base_model_cost_cap, 4096)))

    overload_ratio_permille = int((networks * 1000) // max(1, solve_cap))
    solve_stride = 1
    force_e0 = not bool(e1_enabled)
    defer_noncritical_models = False
    refused_low_priority_connections = 0
    refusal_codes: List[str] = []
    applied_steps: List[int] = []
    decision_log_rows: List[dict] = []

    def _append_step(step_index: int, step_name: str, details: Mapping[str, object]) -> None:
        decision_log_rows.append(
            {
                "decision_id": "decision.elec.degrade.{}".format(
                    canonical_sha256(
                        {
                            "tick": int(tick),
                            "budget_envelope_id": envelope_id,
                            "step_index": int(step_index),
                            "step_name": str(step_name),
                            "details": dict(details or {}),
                        }
                    )[:16]
                ),
                "tick": int(tick),
                "process_id": "process.elec_budget_degrade",
                "budget_envelope_id": envelope_id,
                "step_index": int(step_index),
                "step_name": str(step_name),
                "details": dict(details or {}),
            }
        )

    if overload_ratio_permille > 1000 and bool(e1_enabled):
        solve_stride = int(min(8, max(2, (overload_ratio_permille + 999) // 1000)))
        applied_steps.append(1)
        _append_step(
            1,
            "reduce_e1_solve_frequency",
            {
                "network_count": int(networks),
                "max_network_solves": int(solve_cap),
                "solve_stride": int(solve_stride),
                "overload_ratio_permille": int(overload_ratio_permille),
            },
        )

    if overload_ratio_permille > 1000 and networks > solve_cap:
        applied_steps.append(2)
        _append_step(
            2,
            "downgrade_networks_to_e0",
            {
                "network_count": int(networks),
                "max_network_solves": int(solve_cap),
                "downgrade_count": int(max(0, networks - solve_cap)),
            },
        )

    if overload_ratio_permille > 1500:
        defer_noncritical_models = True
        model_cost_cap = int(max(128, model_cost_cap // 2))
        applied_steps.append(3)
        _append_step(
            3,
            "defer_noncritical_models",
            {
                "model_cost_cap": int(model_cost_cap),
                "overload_ratio_permille": int(overload_ratio_permille),
            },
        )

    if overload_ratio_permille > 2000 and pending_low > 0:
        if bool(strict_profile_enabled):
            refused_low_priority_connections = int(max(0, pending_low))
        else:
            refused_low_priority_connections = int(max(1, pending_low // 2))
        refusal_codes.append(REFUSAL_ELEC_LOW_PRIORITY_CONNECTION)
        applied_steps.append(4)
        _append_step(
            4,
            "refuse_low_priority_connections",
            {
                "pending_low_priority_connections": int(pending_low),
                "refused_low_priority_connections": int(refused_low_priority_connections),
                "strict_profile_enabled": bool(strict_profile_enabled),
            },
        )

    payload = {
        "schema_version": "1.0.0",
        "tick": int(tick),
        "budget_envelope_id": envelope_id,
        "overload_ratio_permille": int(overload_ratio_permille),
        "solve_stride": int(max(1, solve_stride)),
        "force_e0": bool(force_e0),
        "defer_noncritical_models": bool(defer_noncritical_models),
        "model_cost_cap": int(max(1, model_cost_cap)),
        "refused_low_priority_connections": int(max(0, refused_low_priority_connections)),
        "refusal_codes": sorted(set(str(item).strip() for item in refusal_codes if str(item).strip())),
        "applied_steps": list(applied_steps),
        "decision_log_rows": [
            _with_fingerprint(dict(row))
            for row in sorted(
                (dict(row) for row in list(decision_log_rows or []) if isinstance(row, Mapping)),
                key=lambda item: (int(_as_int(item.get("step_index", 0), 0)), str(item.get("decision_id", ""))),
            )
        ],
        "deterministic_fingerprint": "",
    }
    seed = dict(payload)
    seed["decision_log_rows"] = [dict(row) for row in list(payload.get("decision_log_rows") or [])]
    seed["deterministic_fingerprint"] = ""
    payload["deterministic_fingerprint"] = canonical_sha256(seed)
    return payload


__all__ = [
    "REFUSAL_ELEC_LOW_PRIORITY_CONNECTION",
    "apply_elec_budget_degradation",
]
