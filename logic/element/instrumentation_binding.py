"""LOGIC-2 instrumentation bindings for logic elements."""

from __future__ import annotations

from typing import Mapping, Sequence

from meta.instrumentation import (
    generate_measurement_observation,
    resolve_instrumentation_surface,
    route_forensics_request,
)


LOGIC_ELEMENT_INSTRUMENTATION_OWNER_KIND = "logic_element"
LOGIC_ELEMENT_INSTRUMENTATION_DEFAULT_ID = "logic.element.default"


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _rows_from_registry(payload: Mapping[str, object] | None) -> list[dict]:
    body = _as_map(payload)
    rows = body.get("instrumentation_surfaces")
    if not isinstance(rows, list):
        rows = _as_map(body.get("record")).get("instrumentation_surfaces")
    return [dict(item) for item in _as_list(rows) if isinstance(item, Mapping)]


def _materialize_logic_element_surface_payload(
    *,
    element_id: str,
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
) -> dict:
    rows = _rows_from_registry(instrumentation_surface_registry_payload)
    exact = resolve_instrumentation_surface(
        owner_kind=LOGIC_ELEMENT_INSTRUMENTATION_OWNER_KIND,
        owner_id=str(element_id or "").strip(),
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
    )
    if exact:
        return {"instrumentation_surfaces": rows}
    default = resolve_instrumentation_surface(
        owner_kind=LOGIC_ELEMENT_INSTRUMENTATION_OWNER_KIND,
        owner_id=LOGIC_ELEMENT_INSTRUMENTATION_DEFAULT_ID,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
    )
    if not default:
        return {"instrumentation_surfaces": rows}
    materialized = dict(default)
    materialized["owner_id"] = str(element_id or "").strip()
    materialized["extensions"] = dict(_as_map(materialized.get("extensions")), materialized_from=LOGIC_ELEMENT_INSTRUMENTATION_DEFAULT_ID)
    return {"instrumentation_surfaces": rows + [materialized]}


def resolve_logic_element_instrumentation_surface(
    *,
    element_id: str,
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
) -> dict:
    payload = _materialize_logic_element_surface_payload(
        element_id=element_id,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
    )
    return resolve_instrumentation_surface(
        owner_kind=LOGIC_ELEMENT_INSTRUMENTATION_OWNER_KIND,
        owner_id=str(element_id or "").strip(),
        instrumentation_surface_registry_payload=payload,
    )


def observe_logic_element_output_port(
    *,
    element_id: str,
    raw_value: int,
    current_tick: int,
    authority_context: Mapping[str, object] | None,
    has_physical_access: bool,
    available_instrument_type_ids: Sequence[object],
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
    access_policy_registry_payload: Mapping[str, object] | None,
    measurement_model_registry_payload: Mapping[str, object] | None,
) -> dict:
    payload = _materialize_logic_element_surface_payload(
        element_id=element_id,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
    )
    return generate_measurement_observation(
        owner_kind=LOGIC_ELEMENT_INSTRUMENTATION_OWNER_KIND,
        owner_id=str(element_id or "").strip(),
        measurement_point_id="measure.logic.element.output_port",
        raw_value=int(raw_value),
        current_tick=int(current_tick),
        authority_context=authority_context,
        has_physical_access=bool(has_physical_access),
        available_instrument_type_ids=available_instrument_type_ids,
        instrumentation_surface_registry_payload=payload,
        access_policy_registry_payload=access_policy_registry_payload,
        measurement_model_registry_payload=measurement_model_registry_payload,
    )


def observe_logic_element_state_vector(
    *,
    element_id: str,
    raw_value: int,
    current_tick: int,
    authority_context: Mapping[str, object] | None,
    has_physical_access: bool,
    available_instrument_type_ids: Sequence[object],
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
    access_policy_registry_payload: Mapping[str, object] | None,
    measurement_model_registry_payload: Mapping[str, object] | None,
) -> dict:
    payload = _materialize_logic_element_surface_payload(
        element_id=element_id,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
    )
    return generate_measurement_observation(
        owner_kind=LOGIC_ELEMENT_INSTRUMENTATION_OWNER_KIND,
        owner_id=str(element_id or "").strip(),
        measurement_point_id="measure.logic.element.state_vector",
        raw_value=int(raw_value),
        current_tick=int(current_tick),
        authority_context=authority_context,
        has_physical_access=bool(has_physical_access),
        available_instrument_type_ids=available_instrument_type_ids,
        instrumentation_surface_registry_payload=payload,
        access_policy_registry_payload=access_policy_registry_payload,
        measurement_model_registry_payload=measurement_model_registry_payload,
    )


def route_logic_element_forensics(
    *,
    element_id: str,
    forensics_point_id: str,
    authority_context: Mapping[str, object] | None,
    has_physical_access: bool,
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
    access_policy_registry_payload: Mapping[str, object] | None,
    explain_contract_registry_payload: Mapping[str, object] | None,
    event_id: str,
    target_id: str,
    event_kind_id: str,
    truth_hash_anchor: str,
    epistemic_policy_id: str,
    decision_log_rows: object = None,
    safety_event_rows: object = None,
    hazard_rows: object = None,
    compliance_rows: object = None,
    model_result_rows: object = None,
) -> dict:
    payload = _materialize_logic_element_surface_payload(
        element_id=element_id,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
    )
    return route_forensics_request(
        owner_kind=LOGIC_ELEMENT_INSTRUMENTATION_OWNER_KIND,
        owner_id=str(element_id or "").strip(),
        forensics_point_id=str(forensics_point_id or "").strip(),
        authority_context=authority_context,
        has_physical_access=bool(has_physical_access),
        instrumentation_surface_registry_payload=payload,
        access_policy_registry_payload=access_policy_registry_payload,
        explain_contract_registry_payload=explain_contract_registry_payload,
        event_id=str(event_id or "").strip(),
        target_id=str(target_id or "").strip(),
        event_kind_id=str(event_kind_id or "").strip(),
        truth_hash_anchor=str(truth_hash_anchor or "").strip(),
        epistemic_policy_id=str(epistemic_policy_id or "").strip(),
        decision_log_rows=decision_log_rows,
        safety_event_rows=safety_event_rows,
        hazard_rows=hazard_rows,
        compliance_rows=compliance_rows,
        model_result_rows=model_result_rows,
    )


__all__ = [
    "LOGIC_ELEMENT_INSTRUMENTATION_OWNER_KIND",
    "LOGIC_ELEMENT_INSTRUMENTATION_DEFAULT_ID",
    "resolve_logic_element_instrumentation_surface",
    "observe_logic_element_output_port",
    "observe_logic_element_state_vector",
    "route_logic_element_forensics",
]
