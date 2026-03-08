"""LOGIC-7 compute hooks for bounded debug probing and trace capture."""

from __future__ import annotations

from typing import Mapping

from src.meta.compute import request_compute


LOGIC_DEBUG_COMPUTE_OWNER_KIND = "process"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _token(value: object) -> str:
    return str(value or "").strip()


def build_logic_debug_compute_owner_id(*, subject_id: str, phase: str) -> str:
    return "process.logic.debug.{}.{}".format(_token(subject_id) or "logic.subject", _token(phase) or "observe")


def request_logic_debug_compute(
    *,
    current_tick: int,
    subject_id: str,
    phase: str,
    instruction_units: int,
    memory_units: int,
    compute_runtime_state: Mapping[str, object] | None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None,
    compute_budget_profile_id: str = "compute.default",
    owner_priority: int = 140,
    critical: bool = False,
) -> dict:
    return request_compute(
        current_tick=int(max(0, _as_int(current_tick, 0))),
        owner_kind=LOGIC_DEBUG_COMPUTE_OWNER_KIND,
        owner_id=build_logic_debug_compute_owner_id(subject_id=subject_id, phase=phase),
        instruction_units=int(max(1, _as_int(instruction_units, 1))),
        memory_units=int(max(1, _as_int(memory_units, 1))),
        owner_priority=int(max(0, _as_int(owner_priority, 140))),
        critical=bool(critical),
        compute_runtime_state=_as_map(compute_runtime_state),
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_budget_profile_id=_token(compute_budget_profile_id) or "compute.default",
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
    )


__all__ = [
    "LOGIC_DEBUG_COMPUTE_OWNER_KIND",
    "build_logic_debug_compute_owner_id",
    "request_logic_debug_compute",
]
