"""LOGIC-3 instrumentation bindings for logic networks."""

from __future__ import annotations

from typing import Mapping

from src.meta.instrumentation import (
    generate_measurement_observation,
    resolve_instrumentation_surface,
    route_forensics_request,
    validate_control_access,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


LOGIC_NETWORK_INSTRUMENTATION_OWNER_KIND = "logic_network"
LOGIC_NETWORK_INSTRUMENTATION_DEFAULT_ID = "logic.network.default"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _token(value: object) -> str:
    return str(value or "").strip()


def _rows_from_registry(payload: Mapping[str, object] | None) -> list[dict]:
    body = _as_map(payload)
    rows = body.get("instrumentation_surfaces")
    if not isinstance(rows, list):
        rows = _as_map(body.get("record")).get("instrumentation_surfaces")
    return [dict(item) for item in _as_list(rows) if isinstance(item, Mapping)]


def _materialize_logic_network_surface_payload(
    *,
    network_id: str,
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
) -> dict:
    rows = _rows_from_registry(instrumentation_surface_registry_payload)
    exact = resolve_instrumentation_surface(
        owner_kind=LOGIC_NETWORK_INSTRUMENTATION_OWNER_KIND,
        owner_id=_token(network_id),
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
    )
    if exact:
        return {"instrumentation_surfaces": rows}
    default = resolve_instrumentation_surface(
        owner_kind=LOGIC_NETWORK_INSTRUMENTATION_OWNER_KIND,
        owner_id=LOGIC_NETWORK_INSTRUMENTATION_DEFAULT_ID,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
    )
    if not default:
        return {"instrumentation_surfaces": rows}
    materialized = dict(default)
    materialized["owner_id"] = _token(network_id)
    materialized["extensions"] = dict(_as_map(materialized.get("extensions")), materialized_from=LOGIC_NETWORK_INSTRUMENTATION_DEFAULT_ID)
    return {"instrumentation_surfaces": rows + [materialized]}


def resolve_logic_network_instrumentation_surface(
    *,
    network_id: str,
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
) -> dict:
    payload = _materialize_logic_network_surface_payload(
        network_id=network_id,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
    )
    return resolve_instrumentation_surface(
        owner_kind=LOGIC_NETWORK_INSTRUMENTATION_OWNER_KIND,
        owner_id=_token(network_id),
        instrumentation_surface_registry_payload=payload,
    )


def authorize_logic_network_topology_view(
    *,
    network_id: str,
    authority_context: Mapping[str, object] | None,
    has_physical_access: bool,
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
    access_policy_registry_payload: Mapping[str, object] | None,
    control_point_id: str = "control.logic.network.inspect",
) -> dict:
    payload = _materialize_logic_network_surface_payload(
        network_id=network_id,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
    )
    return validate_control_access(
        owner_kind=LOGIC_NETWORK_INSTRUMENTATION_OWNER_KIND,
        owner_id=_token(network_id),
        control_point_id=_token(control_point_id) or "control.logic.network.inspect",
        authority_context=authority_context,
        has_physical_access=has_physical_access,
        instrumentation_surface_registry_payload=payload,
        access_policy_registry_payload=access_policy_registry_payload,
    )


def _measurement_value(payload: Mapping[str, object]) -> int:
    digest = canonical_sha256(_as_map(payload))
    return int(digest[:8], 16)


def observe_logic_network_node(
    *,
    network_id: str,
    node_row: Mapping[str, object],
    current_tick: int,
    authority_context: Mapping[str, object] | None,
    has_physical_access: bool,
    available_instrument_type_ids: object,
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
    access_policy_registry_payload: Mapping[str, object] | None,
    measurement_model_registry_payload: Mapping[str, object] | None,
    measurement_point_id: str = "measure.logic.network.node",
) -> dict:
    payload = _materialize_logic_network_surface_payload(
        network_id=network_id,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
    )
    measurement = generate_measurement_observation(
        owner_kind=LOGIC_NETWORK_INSTRUMENTATION_OWNER_KIND,
        owner_id=_token(network_id),
        measurement_point_id=_token(measurement_point_id) or "measure.logic.network.node",
        raw_value=_measurement_value(node_row),
        current_tick=int(max(0, _as_int(current_tick, 0))),
        authority_context=authority_context,
        has_physical_access=has_physical_access,
        available_instrument_type_ids=available_instrument_type_ids,
        instrumentation_surface_registry_payload=payload,
        access_policy_registry_payload=access_policy_registry_payload,
        measurement_model_registry_payload=measurement_model_registry_payload,
    )
    if str(measurement.get("result", "")) != "complete":
        return dict(measurement)
    artifact = {
        "artifact_id": "artifact.observation.logic_network_node.{}".format(
            canonical_sha256(
                {
                    "network_id": _token(network_id),
                    "node_id": _token(node_row.get("node_id")),
                    "tick": int(max(0, _as_int(current_tick, 0))),
                }
            )[:16]
        ),
        "artifact_family_id": "OBSERVATION",
        "artifact_type_id": "artifact.logic.network_node_observation",
        "network_id": _token(network_id),
        "node_id": _token(node_row.get("node_id")),
        "measurement_artifact_id": _token(_as_map(measurement.get("observation_artifact")).get("artifact_id")),
        "deterministic_fingerprint": "",
        "extensions": {
            "trace_compactable": True,
        },
    }
    artifact["deterministic_fingerprint"] = canonical_sha256(dict(artifact, deterministic_fingerprint=""))
    return {
        "result": "complete",
        "reason_code": "",
        "measurement_observation": dict(measurement),
        "network_node_observation_artifact": artifact,
    }


def observe_logic_network_edge(
    *,
    network_id: str,
    edge_row: Mapping[str, object],
    current_tick: int,
    authority_context: Mapping[str, object] | None,
    has_physical_access: bool,
    available_instrument_type_ids: object,
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
    access_policy_registry_payload: Mapping[str, object] | None,
    measurement_model_registry_payload: Mapping[str, object] | None,
    measurement_point_id: str = "measure.logic.network.edge",
) -> dict:
    payload = _materialize_logic_network_surface_payload(
        network_id=network_id,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
    )
    measurement = generate_measurement_observation(
        owner_kind=LOGIC_NETWORK_INSTRUMENTATION_OWNER_KIND,
        owner_id=_token(network_id),
        measurement_point_id=_token(measurement_point_id) or "measure.logic.network.edge",
        raw_value=_measurement_value(edge_row),
        current_tick=int(max(0, _as_int(current_tick, 0))),
        authority_context=authority_context,
        has_physical_access=has_physical_access,
        available_instrument_type_ids=available_instrument_type_ids,
        instrumentation_surface_registry_payload=payload,
        access_policy_registry_payload=access_policy_registry_payload,
        measurement_model_registry_payload=measurement_model_registry_payload,
    )
    if str(measurement.get("result", "")) != "complete":
        return dict(measurement)
    artifact = {
        "artifact_id": "artifact.observation.logic_network_edge.{}".format(
            canonical_sha256(
                {
                    "network_id": _token(network_id),
                    "edge_id": _token(edge_row.get("edge_id")),
                    "tick": int(max(0, _as_int(current_tick, 0))),
                }
            )[:16]
        ),
        "artifact_family_id": "OBSERVATION",
        "artifact_type_id": "artifact.logic.network_edge_observation",
        "network_id": _token(network_id),
        "edge_id": _token(edge_row.get("edge_id")),
        "measurement_artifact_id": _token(_as_map(measurement.get("observation_artifact")).get("artifact_id")),
        "deterministic_fingerprint": "",
        "extensions": {
            "trace_compactable": True,
        },
    }
    artifact["deterministic_fingerprint"] = canonical_sha256(dict(artifact, deterministic_fingerprint=""))
    return {
        "result": "complete",
        "reason_code": "",
        "measurement_observation": dict(measurement),
        "network_edge_observation_artifact": artifact,
    }


def route_logic_network_forensics(
    *,
    network_id: str,
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
    payload = _materialize_logic_network_surface_payload(
        network_id=network_id,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
    )
    return route_forensics_request(
        owner_kind=LOGIC_NETWORK_INSTRUMENTATION_OWNER_KIND,
        owner_id=_token(network_id),
        forensics_point_id=_token(forensics_point_id),
        authority_context=authority_context,
        has_physical_access=has_physical_access,
        instrumentation_surface_registry_payload=payload,
        access_policy_registry_payload=access_policy_registry_payload,
        explain_contract_registry_payload=explain_contract_registry_payload,
        event_id=_token(event_id),
        target_id=_token(target_id),
        event_kind_id=_token(event_kind_id),
        truth_hash_anchor=_token(truth_hash_anchor),
        epistemic_policy_id=_token(epistemic_policy_id),
        decision_log_rows=decision_log_rows,
        safety_event_rows=safety_event_rows,
        hazard_rows=hazard_rows,
        compliance_rows=compliance_rows,
        model_result_rows=model_result_rows,
    )


__all__ = [
    "LOGIC_NETWORK_INSTRUMENTATION_OWNER_KIND",
    "LOGIC_NETWORK_INSTRUMENTATION_DEFAULT_ID",
    "authorize_logic_network_topology_view",
    "observe_logic_network_edge",
    "observe_logic_network_node",
    "resolve_logic_network_instrumentation_surface",
    "route_logic_network_forensics",
]
