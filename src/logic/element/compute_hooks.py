"""LOGIC-2 compute-budget hooks for future element evaluation."""

from __future__ import annotations

from typing import Mapping

from src.meta.compute import request_compute
from src.system import state_vector_definition_rows_by_owner


LOGIC_ELEMENT_COMPUTE_OWNER_KIND = "process"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _token(value: object) -> str:
    return str(value or "").strip()


def _state_vector_memory_units(*, element_id: str, state_vector_definition_rows: object) -> int:
    definition = dict(state_vector_definition_rows_by_owner(state_vector_definition_rows).get(_token(element_id)) or {})
    fields = list(definition.get("state_fields") or [])
    return int(max(1, len(fields) * 2 if fields else 1))


def build_logic_element_compute_owner_id(*, element_id: str, network_id: str | None = None) -> str:
    element_token = _token(element_id) or "logic.element"
    network_token = _token(network_id)
    if network_token:
        return "process.logic.evaluate.{}.{}".format(network_token, element_token)
    return "process.logic.evaluate.{}".format(element_token)


def request_logic_element_compute(
    *,
    current_tick: int,
    element_row: Mapping[str, object],
    state_vector_definition_rows: object,
    compute_runtime_state: Mapping[str, object] | None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None,
    compute_budget_profile_id: str = "compute.default",
    network_id: str | None = None,
    owner_priority: int = 100,
    critical: bool = False,
) -> dict:
    element_id = _token(_as_map(element_row).get("element_id"))
    instruction_units = int(max(1, _as_int(_as_map(element_row).get("compute_cost_units"), 1)))
    memory_units = _state_vector_memory_units(
        element_id=element_id,
        state_vector_definition_rows=state_vector_definition_rows,
    )
    result = request_compute(
        current_tick=int(max(0, _as_int(current_tick, 0))),
        owner_kind=LOGIC_ELEMENT_COMPUTE_OWNER_KIND,
        owner_id=build_logic_element_compute_owner_id(element_id=element_id, network_id=network_id),
        instruction_units=instruction_units,
        memory_units=memory_units,
        owner_priority=int(max(0, _as_int(owner_priority, 100))),
        critical=bool(critical),
        compute_runtime_state=compute_runtime_state,
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_budget_profile_id=_token(compute_budget_profile_id) or "compute.default",
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
    )
    result["extensions"] = {
        "element_id": element_id,
        "network_id": _token(network_id) or None,
        "instruction_units_requested": instruction_units,
        "memory_units_requested": memory_units,
    }
    return result


__all__ = [
    "LOGIC_ELEMENT_COMPUTE_OWNER_KIND",
    "build_logic_element_compute_owner_id",
    "request_logic_element_compute",
]
