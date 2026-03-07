"""LOGIC-1 signal observation helpers gated by META-INSTR."""

from __future__ import annotations

from typing import Mapping

from src.meta.instrumentation import generate_measurement_observation, validate_control_access
from tools.xstack.compatx.canonical_json import canonical_sha256

from src.logic.signal.signal_store import REFUSAL_SIGNAL_INVALID, normalize_signal_store_state


def _as_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _token(value: object) -> str:
    return str(value or "").strip()


def _slot_key(network_id: str, element_id: str, port_id: str) -> str:
    return "|".join((_token(network_id), _token(element_id), _token(port_id)))


def _slot_from_row(signal_row: Mapping[str, object]) -> str:
    slot = _as_map(_as_map(signal_row.get("extensions")).get("slot"))
    return _slot_key(_token(slot.get("network_id")), _token(slot.get("element_id")), _token(slot.get("port_id")))


def _measurement_value_for_signal(signal_row: Mapping[str, object]) -> int:
    value_ref = _as_map(signal_row.get("value_ref"))
    kind = _token(value_ref.get("value_kind"))
    if kind == "boolean":
        return int(max(0, _as_int(value_ref.get("value", 0), 0)))
    if kind == "scalar":
        return int(_as_int(value_ref.get("value_fixed", 0), 0))
    digest = canonical_sha256(value_ref)
    return int(digest[:8], 16)


def authorize_logic_probe_control(
    *,
    control_point_id: str,
    authority_context: Mapping[str, object] | None,
    has_physical_access: bool,
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
    access_policy_registry_payload: Mapping[str, object] | None,
) -> dict:
    return validate_control_access(
        owner_kind="domain",
        owner_id="domain.logic",
        control_point_id=_token(control_point_id),
        authority_context=authority_context,
        has_physical_access=has_physical_access,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
        access_policy_registry_payload=access_policy_registry_payload,
    )


def observe_signal_row(
    *,
    signal_row: Mapping[str, object],
    current_tick: int,
    authority_context: Mapping[str, object] | None,
    has_physical_access: bool,
    available_instrument_type_ids: object,
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
    access_policy_registry_payload: Mapping[str, object] | None,
    measurement_model_registry_payload: Mapping[str, object] | None,
    measurement_point_id: str = "measure.logic.signal",
) -> dict:
    row = _as_map(signal_row)
    signal_id = _token(row.get("signal_id"))
    if not signal_id:
        return {"result": "refused", "reason_code": REFUSAL_SIGNAL_INVALID}
    measurement = generate_measurement_observation(
        owner_kind="domain",
        owner_id="domain.logic",
        measurement_point_id=_token(measurement_point_id) or "measure.logic.signal",
        raw_value=_measurement_value_for_signal(row),
        current_tick=int(max(0, _as_int(current_tick, 0))),
        authority_context=authority_context,
        has_physical_access=has_physical_access,
        available_instrument_type_ids=available_instrument_type_ids,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
        access_policy_registry_payload=access_policy_registry_payload,
        measurement_model_registry_payload=measurement_model_registry_payload,
    )
    if str(measurement.get("result", "")) != "complete":
        return dict(measurement)
    artifact = {
        "artifact_id": "artifact.observation.logic_signal.{}".format(
            canonical_sha256(
                {
                    "signal_id": signal_id,
                    "tick": int(max(0, _as_int(current_tick, 0))),
                    "measurement_artifact_id": str(dict(measurement.get("observation_artifact") or {}).get("artifact_id", "")).strip(),
                }
            )[:16]
        ),
        "artifact_family_id": "OBSERVATION",
        "artifact_type_id": "artifact.logic.signal_observation",
        "signal_id": signal_id,
        "signal_type_id": _token(row.get("signal_type_id")),
        "carrier_type_id": _token(row.get("carrier_type_id")),
        "tick": int(max(0, _as_int(current_tick, 0))),
        "measurement_artifact_id": str(dict(measurement.get("observation_artifact") or {}).get("artifact_id", "")).strip(),
        "observed_value_ref": dict(_as_map(row.get("value_ref"))),
        "signal_hash": canonical_sha256(row),
        "deterministic_fingerprint": "",
        "extensions": {
            "trace_compactable": True,
            "slot_key": _slot_from_row(row),
        },
    }
    artifact["deterministic_fingerprint"] = canonical_sha256(dict(artifact, deterministic_fingerprint=""))
    return {
        "result": "complete",
        "reason_code": "",
        "measurement_observation": dict(measurement),
        "signal_observation_artifact": artifact,
    }


def observe_signal_store_slot(
    *,
    signal_store_state: Mapping[str, object] | None,
    network_id: str,
    element_id: str,
    port_id: str,
    current_tick: int,
    authority_context: Mapping[str, object] | None,
    has_physical_access: bool,
    available_instrument_type_ids: object,
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
    access_policy_registry_payload: Mapping[str, object] | None,
    measurement_model_registry_payload: Mapping[str, object] | None,
    measurement_point_id: str = "measure.logic.signal",
) -> dict:
    state = normalize_signal_store_state(signal_store_state)
    slot_key = _slot_key(network_id, element_id, port_id)
    selected = {}
    tick = int(max(0, _as_int(current_tick, 0)))
    for row in state.get("signal_rows") or []:
        if _slot_from_row(row) != slot_key:
            continue
        start_tick = _as_int(row.get("valid_from_tick", 0), 0)
        end_tick = row.get("valid_until_tick")
        end_value = None if end_tick is None else _as_int(end_tick, start_tick)
        if start_tick > tick or (end_value is not None and tick >= end_value):
            continue
        if not selected or (_as_int(selected.get("valid_from_tick", 0), 0), _token(selected.get("signal_id"))) <= (start_tick, _token(row.get("signal_id"))):
            selected = dict(row)
    if not selected:
        return {"result": "refused", "reason_code": REFUSAL_SIGNAL_INVALID}
    return observe_signal_row(
        signal_row=selected,
        current_tick=tick,
        authority_context=authority_context,
        has_physical_access=has_physical_access,
        available_instrument_type_ids=available_instrument_type_ids,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
        access_policy_registry_payload=access_policy_registry_payload,
        measurement_model_registry_payload=measurement_model_registry_payload,
        measurement_point_id=measurement_point_id,
    )


__all__ = [
    "authorize_logic_probe_control",
    "observe_signal_row",
    "observe_signal_store_slot",
]
