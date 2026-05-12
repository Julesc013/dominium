"""LOGIC-5 compute hooks for bounded timing analysis."""

from __future__ import annotations

from typing import Mapping

from meta.compute import request_compute


LOGIC_TIMING_COMPUTE_OWNER_KIND = "process"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _token(value: object) -> str:
    return str(value or "").strip()


def build_logic_timing_compute_owner_id(*, network_id: str, phase: str) -> str:
    return "process.logic.timing.{}.{}".format(_token(network_id) or "logic.network", _token(phase) or "analysis")


def request_logic_timing_compute(
    *,
    current_tick: int,
    network_id: str,
    phase: str,
    instruction_units: int,
    compute_runtime_state: Mapping[str, object] | None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None,
    compute_budget_profile_id: str = "compute.default",
    owner_priority: int = 120,
    critical: bool = False,
) -> dict:
    return request_compute(
        current_tick=int(max(0, _as_int(current_tick, 0))),
        owner_kind=LOGIC_TIMING_COMPUTE_OWNER_KIND,
        owner_id=build_logic_timing_compute_owner_id(network_id=network_id, phase=phase),
        instruction_units=int(max(1, _as_int(instruction_units, 1))),
        memory_units=1,
        owner_priority=int(max(0, _as_int(owner_priority, 120))),
        critical=bool(critical),
        compute_runtime_state=_as_map(compute_runtime_state),
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_budget_profile_id=_token(compute_budget_profile_id) or "compute.default",
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
    )


__all__ = [
    "LOGIC_TIMING_COMPUTE_OWNER_KIND",
    "build_logic_timing_compute_owner_id",
    "request_logic_timing_compute",
]
