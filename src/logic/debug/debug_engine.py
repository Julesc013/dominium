"""LOGIC-7 deterministic debug probing, trace capture, and protocol-summary hooks."""

from __future__ import annotations

from typing import Dict, Mapping, Sequence

from src.logic.compile import (
    build_logic_compiled_forced_expand_event,
    build_logic_compiled_introspection_artifact,
)
from src.logic.element.instrumentation_binding import (
    observe_logic_element_output_port,
    observe_logic_element_state_vector,
)
from src.logic.network.instrumentation_binding import (
    observe_logic_network_compiled_summary,
    observe_logic_network_edge,
    observe_logic_network_node,
)
from src.logic.signal import normalize_signal_store_state, observe_signal_row
from src.meta.explain import build_explain_artifact, normalize_explain_artifact_rows
from src.meta.instrumentation import generate_measurement_observation
from tools.xstack.compatx.canonical_json import canonical_sha256

from .compute_hooks import request_logic_debug_compute
from .runtime_state import (
    build_logic_debug_probe_request_row,
    build_logic_debug_trace_artifact_row,
    build_logic_debug_trace_request_row,
    build_logic_debug_trace_session_row,
    normalize_logic_debug_state,
)


PROCESS_LOGIC_PROBE = "process.logic_probe"
PROCESS_LOGIC_TRACE_START = "process.logic_trace_start"
PROCESS_LOGIC_TRACE_TICK = "process.logic_trace_tick"
PROCESS_LOGIC_TRACE_END = "process.logic_trace_end"

REFUSAL_LOGIC_DEBUG_INVALID_REQUEST = "refusal.logic.debug_invalid_request"
REFUSAL_LOGIC_DEBUG_ACCESS_DENIED = "refusal.logic.debug_access_denied"
REFUSAL_LOGIC_DEBUG_SUBJECT_NOT_FOUND = "refusal.logic.debug_subject_not_found"
REFUSAL_LOGIC_DEBUG_SAMPLING_POLICY_UNREGISTERED = "refusal.logic.debug_sampling_policy_unregistered"
REFUSAL_LOGIC_DEBUG_TRACE_BOUNDS_EXCEEDED = "refusal.logic.debug_trace_bounds_exceeded"
REFUSAL_LOGIC_DEBUG_TRACE_SESSION_NOT_FOUND = "refusal.logic.debug_trace_session_not_found"
REFUSAL_LOGIC_DEBUG_REQUIRES_EXPAND = "refusal.logic.debug_requires_expand"
REFUSAL_LOGIC_DEBUG_PROTOCOL_UNAVAILABLE = "refusal.logic.debug_protocol_unavailable"

_BOUNDARY_MEASUREMENT_POINTS = {
    "measure.logic.signal",
    "measure.logic.bus",
    "measure.logic.protocol_frame",
    "measure.logic.element.output_port",
    "measure.logic.network.compiled_summary",
}
_INTERNAL_MEASUREMENT_POINTS = {
    "measure.logic.timing_trace",
    "measure.logic.element.state_vector",
    "measure.logic.network.node",
    "measure.logic.network.edge",
}


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


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda item: str(item)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _rows_from_registry(payload: Mapping[str, object] | None, keys: Sequence[str]) -> list[dict]:
    body = _as_map(payload)
    for key in keys:
        rows = body.get(key)
        if isinstance(rows, list):
            return [dict(item) for item in rows if isinstance(item, Mapping)]
    record = _as_map(body.get("record"))
    for key in keys:
        rows = record.get(key)
        if isinstance(rows, list):
            return [dict(item) for item in rows if isinstance(item, Mapping)]
    return []


def _rows_by_id(rows: object, key: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in _as_list(rows) if isinstance(item, Mapping)),
        key=lambda item: _token(item.get(key)),
    ):
        token = _token(row.get(key))
        if token:
            out[token] = dict(row)
    return dict((name, dict(out[name])) for name in sorted(out.keys()))


def _logic_binding_by_network_id(logic_network_state: Mapping[str, object] | None) -> Dict[str, dict]:
    return _rows_by_id(_as_map(logic_network_state).get("logic_network_binding_rows"), "network_id")


def _logic_graph_by_id(logic_network_state: Mapping[str, object] | None) -> Dict[str, dict]:
    return _rows_by_id(_as_map(logic_network_state).get("logic_network_graph_rows"), "graph_id")


def _debug_sampling_policy_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    return _rows_by_id(_rows_from_registry(payload, ("debug_sampling_policies",)), "policy_id")


def _compiled_model_rows_by_id(rows: object) -> Dict[str, dict]:
    return _rows_by_id(rows, "compiled_model_id")


def _select_active_signal_row(
    *,
    signal_store_state: Mapping[str, object] | None,
    network_id: str,
    element_id: str,
    port_id: str,
    tick: int,
) -> dict:
    state = normalize_signal_store_state(signal_store_state)
    selected = {}
    for row in state.get("signal_rows") or []:
        signal_row = dict(row)
        slot = _as_map(_as_map(signal_row.get("extensions")).get("slot"))
        if (
            _token(slot.get("network_id")) != _token(network_id)
            or _token(slot.get("element_id")) != _token(element_id)
            or _token(slot.get("port_id")) != _token(port_id)
        ):
            continue
        start_tick = _as_int(signal_row.get("valid_from_tick"), 0)
        end_tick = signal_row.get("valid_until_tick")
        end_value = None if end_tick is None else _as_int(end_tick, start_tick)
        if start_tick > tick or (end_value is not None and tick >= end_value):
            continue
        if not selected or (_as_int(selected.get("valid_from_tick"), 0), _token(selected.get("signal_id"))) <= (
            start_tick,
            _token(signal_row.get("signal_id")),
        ):
            selected = signal_row
    return selected


def _measurement_value_for_signal(signal_row: Mapping[str, object]) -> int:
    value_ref = _as_map(signal_row.get("value_ref"))
    value_kind = _token(value_ref.get("value_kind"))
    if value_kind == "boolean":
        return 1 if bool(_as_int(value_ref.get("value"), 0)) else 0
    if value_kind == "scalar":
        return int(_as_int(value_ref.get("value_fixed"), 0))
    return int(canonical_sha256(_canon(value_ref))[:8], 16)


def _sample_target_key(target: Mapping[str, object]) -> str:
    return "|".join(
        (
            _token(target.get("measurement_point_id")),
            _token(target.get("subject_id")),
            _token(target.get("network_id")),
            _token(target.get("element_id")),
            _token(target.get("port_id")),
            _token(target.get("node_id")),
            _token(target.get("edge_id")),
        )
    )


def _targets_from_trace_request(request_row: Mapping[str, object]) -> list[dict]:
    request = _as_map(request_row)
    extensions = _as_map(request.get("extensions"))
    raw_targets = [
        dict(item)
        for item in _as_list(extensions.get("targets"))
        if isinstance(item, Mapping)
    ]
    targets = []
    if raw_targets:
        for row in raw_targets:
            target = dict(row)
            target["subject_id"] = _token(target.get("subject_id")) or _token(request.get("subject_id"))
            target["measurement_point_id"] = _token(target.get("measurement_point_id"))
            target["target_key"] = _sample_target_key(target)
            if target["measurement_point_id"]:
                targets.append(target)
    else:
        for measurement_point_id in _as_list(request.get("measurement_point_ids")):
            target = {
                "subject_id": _token(request.get("subject_id")),
                "measurement_point_id": _token(measurement_point_id),
            }
            target["target_key"] = _sample_target_key(target)
            targets.append(target)
    return sorted(
        (dict(row) for row in targets if _token(row.get("measurement_point_id"))),
        key=lambda row: (_token(row.get("measurement_point_id")), _token(row.get("target_key"))),
    )


def _compiled_capsule_id(network_id: str) -> str:
    return "capsule.logic_controller.{}".format(canonical_sha256({"network_id": _token(network_id)})[:16])


def _compiled_binding_context(
    *,
    logic_network_state: Mapping[str, object] | None,
    compiled_model_rows: object,
    network_id: str,
) -> dict:
    binding_row = dict(_logic_binding_by_network_id(logic_network_state).get(_token(network_id)) or {})
    compiled_model_id = _token(_as_map(binding_row.get("extensions")).get("compiled_model_id"))
    compiled_row = dict(_compiled_model_rows_by_id(compiled_model_rows).get(compiled_model_id) or {})
    return {
        "binding_row": binding_row,
        "compiled_model_id": compiled_model_id,
        "compiled_model_row": compiled_row,
        "compiled_debug_active": bool(compiled_model_id and compiled_row),
    }


def _latest_network_events(
    *,
    rows: object,
    network_id: str,
    tick: int,
    primary_key: str,
) -> list[dict]:
    filtered = []
    for row in sorted(
        (dict(item) for item in _as_list(rows) if isinstance(item, Mapping)),
        key=lambda item: (_as_int(item.get("tick"), 0), _token(item.get(primary_key))),
    ):
        if _token(row.get("network_id")) != _token(network_id):
            continue
        if _as_int(row.get("tick"), 0) > int(max(0, _as_int(tick, 0))):
            continue
        filtered.append(row)
    return filtered


def _timing_summary_artifact(
    *,
    network_id: str,
    current_tick: int,
    logic_eval_state: Mapping[str, object] | None,
    authority_context: Mapping[str, object] | None,
    has_physical_access: bool,
    available_instrument_type_ids: object,
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
    access_policy_registry_payload: Mapping[str, object] | None,
    measurement_model_registry_payload: Mapping[str, object] | None,
) -> dict:
    eval_state = _as_map(logic_eval_state)
    oscillation_rows = _latest_network_events(
        rows=eval_state.get("logic_oscillation_record_rows"),
        network_id=network_id,
        tick=current_tick,
        primary_key="record_id",
    )
    timing_violation_rows = _latest_network_events(
        rows=eval_state.get("logic_timing_violation_event_rows"),
        network_id=network_id,
        tick=current_tick,
        primary_key="event_id",
    )
    watchdog_rows = _latest_network_events(
        rows=eval_state.get("logic_watchdog_timeout_event_rows"),
        network_id=network_id,
        tick=current_tick,
        primary_key="event_id",
    )
    state_update_rows = _latest_network_events(
        rows=eval_state.get("logic_state_update_record_rows"),
        network_id=network_id,
        tick=current_tick,
        primary_key="update_id",
    )
    summary = {
        "network_id": _token(network_id),
        "tick": int(max(0, _as_int(current_tick, 0))),
        "latest_period_ticks": int(max(0, _as_int((_as_map(oscillation_rows[-1]) if oscillation_rows else {}).get("period_ticks"), 0))),
        "oscillation_record_count": int(len(oscillation_rows)),
        "timing_violation_count": int(len(timing_violation_rows)),
        "watchdog_timeout_count": int(len(watchdog_rows)),
        "last_state_transition_ids": [
            _token(row.get("update_id"))
            for row in state_update_rows[-8:]
            if _token(row.get("update_id"))
        ],
    }
    measurement = generate_measurement_observation(
        owner_kind="domain",
        owner_id="domain.logic",
        measurement_point_id="measure.logic.timing_trace",
        raw_value=int(canonical_sha256(_canon(summary))[:8], 16),
        current_tick=int(max(0, _as_int(current_tick, 0))),
        authority_context=authority_context,
        has_physical_access=bool(has_physical_access),
        available_instrument_type_ids=available_instrument_type_ids,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
        access_policy_registry_payload=access_policy_registry_payload,
        measurement_model_registry_payload=measurement_model_registry_payload,
    )
    if _token(measurement.get("result")) != "complete":
        return dict(measurement)
    artifact = {
        "artifact_id": "artifact.logic.timing_summary.{}".format(
            canonical_sha256(
                {
                    "network_id": _token(network_id),
                    "tick": int(max(0, _as_int(current_tick, 0))),
                    "measurement_artifact_id": _token(_as_map(measurement.get("observation_artifact")).get("artifact_id")),
                }
            )[:16]
        ),
        "artifact_family_id": "OBSERVATION",
        "artifact_type_id": "artifact.logic.timing_summary",
        "network_id": _token(network_id),
        "tick": int(max(0, _as_int(current_tick, 0))),
        "measurement_artifact_id": _token(_as_map(measurement.get("observation_artifact")).get("artifact_id")),
        "deterministic_fingerprint": "",
        "extensions": dict(_canon(summary), trace_compactable=True),
    }
    artifact["deterministic_fingerprint"] = canonical_sha256(dict(artifact, deterministic_fingerprint=""))
    return {
        "result": "complete",
        "measurement_observation": dict(measurement),
        "timing_summary_artifact": artifact,
        "sample_value_row": {
            "measurement_point_id": "measure.logic.timing_trace",
            "target_key": _token(network_id),
            "measurement_artifact_id": _token(_as_map(measurement.get("observation_artifact")).get("artifact_id")),
            "observation_artifact_id": _token(artifact.get("artifact_id")),
            "value": _as_map(measurement.get("observation_artifact")).get("value"),
            "value_hash": canonical_sha256(_canon(summary)),
        },
    }


def _build_protocol_summary_artifact(
    *,
    signal_row: Mapping[str, object],
    signal_store_state: Mapping[str, object] | None,
    protocol_registry_payload: Mapping[str, object] | None,
    current_tick: int,
) -> dict:
    row = dict(signal_row)
    signal_ext = _as_map(row.get("extensions"))
    protocol_id = _token(signal_ext.get("protocol_id"))
    bus_id = _token(signal_ext.get("bus_id"))
    if (not protocol_id) or (not bus_id):
        return {}
    protocol_registry = _rows_by_id(_rows_from_registry(protocol_registry_payload, ("protocols",)), "protocol_id")
    protocol_row = dict(protocol_registry.get(protocol_id) or {})
    bus_rows = _rows_by_id(normalize_signal_store_state(signal_store_state).get("bus_definition_rows"), "bus_id")
    bus_row = dict(bus_rows.get(bus_id) or {})
    if not protocol_row or not bus_row:
        return {}
    value_ref = _as_map(row.get("value_ref"))
    if _token(value_ref.get("value_kind")) != "bus":
        return {}
    fields = [
        _canon(dict(item))
        for item in sorted(
            (dict(item) for item in _as_list(bus_row.get("fields")) if isinstance(item, Mapping)),
            key=lambda item: _token(item.get("field_id")),
        )
    ]
    sub_signals = [
        _canon(dict(item) if isinstance(item, Mapping) else {"value": item})
        for item in _as_list(value_ref.get("sub_signals"))[:16]
    ]
    artifact = {
        "artifact_id": "artifact.logic.protocol_summary.{}".format(
            canonical_sha256(
                {
                    "signal_id": _token(row.get("signal_id")),
                    "protocol_id": protocol_id,
                    "tick": int(max(0, _as_int(current_tick, 0))),
                }
            )[:16]
        ),
        "artifact_family_id": "OBSERVATION",
        "artifact_type_id": "artifact.logic.protocol_summary",
        "signal_id": _token(row.get("signal_id")),
        "protocol_id": protocol_id,
        "bus_id": bus_id,
        "tick": int(max(0, _as_int(current_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": {
            "protocol_description": _token(protocol_row.get("description")),
            "encoding_id": _token(bus_row.get("encoding_id")),
            "fields": fields[:16],
            "frame_excerpt": sub_signals,
            "packed_fixed": value_ref.get("packed_fixed"),
            "trace_compactable": True,
        },
    }
    artifact["deterministic_fingerprint"] = canonical_sha256(dict(artifact, deterministic_fingerprint=""))
    return artifact


def _probe_artifact(
    *,
    request_row: Mapping[str, object],
    current_tick: int,
    measurement_artifact_id: str,
    sample_value_row: Mapping[str, object],
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "artifact_id": "artifact.logic.debug_probe.{}".format(
            canonical_sha256(
                {
                    "request_id": _token(request_row.get("request_id")),
                    "measurement_point_id": _token(request_row.get("measurement_point_id")),
                    "tick": int(max(0, _as_int(current_tick, 0))),
                    "sample_value_row": _canon(_as_map(sample_value_row)),
                }
            )[:16]
        ),
        "artifact_family_id": "OBSERVATION",
        "artifact_type_id": "artifact.logic.debug_probe",
        "request_id": _token(request_row.get("request_id")),
        "subject_id": _token(request_row.get("subject_id")),
        "measurement_point_id": _token(request_row.get("measurement_point_id")),
        "tick": int(max(0, _as_int(current_tick, 0))),
        "measurement_artifact_id": _token(measurement_artifact_id),
        "deterministic_fingerprint": "",
        "extensions": dict(_canon(_as_map(sample_value_row)), trace_compactable=True, **_canon(_as_map(extensions))),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _debug_explain(
    *,
    explain_kind_id: str,
    target_id: str,
    event_id_seed: Mapping[str, object],
    remediation_hints: Sequence[object],
    extensions: Mapping[str, object] | None = None,
) -> dict:
    seed = _canon(_as_map(event_id_seed))
    event_id = "event.logic.debug.{}".format(canonical_sha256({"kind": explain_kind_id, "seed": seed})[:16])
    return build_explain_artifact(
        explain_id="{}.{}".format(
            _token(explain_kind_id),
            canonical_sha256({"target_id": _token(target_id), "seed": seed})[:16],
        ),
        event_id=event_id,
        target_id=_token(target_id),
        cause_chain=["cause.logic.debug"],
        remediation_hints=list(remediation_hints),
        extensions=dict(_canon(_as_map(extensions)), event_kind_id=_token(explain_kind_id)),
    )


def _remote_debug_allowed(
    *,
    has_physical_access: bool,
    remote_mode: str,
    request_extensions: Mapping[str, object],
) -> tuple[bool, str]:
    if bool(has_physical_access):
        return True, ""
    mode = _token(remote_mode) or "sig_authorized_only"
    if mode == "forbidden":
        return False, REFUSAL_LOGIC_DEBUG_ACCESS_DENIED
    if mode == "sig_authorized_only":
        if _token(_as_map(request_extensions).get("remote_authorization_artifact_id")):
            return True, ""
        return False, REFUSAL_LOGIC_DEBUG_ACCESS_DENIED
    return True, ""


def _prepare_compiled_debug_access(
    *,
    current_tick: int,
    network_id: str,
    targets: Sequence[Mapping[str, object]],
    allow_force_expand: bool,
    debug_state: Mapping[str, object] | None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None,
    compute_budget_profile_id: str,
    logic_network_state: Mapping[str, object] | None,
    compiled_model_rows: object,
) -> dict:
    compiled_context = _compiled_binding_context(
        logic_network_state=logic_network_state,
        compiled_model_rows=compiled_model_rows,
        network_id=network_id,
    )
    if not bool(compiled_context.get("compiled_debug_active", False)):
        return {
            "result": "complete",
            "compute_runtime_state": _as_map(_as_map(debug_state).get("compute_runtime_state")),
            "forced_expand_event_rows": [],
            "explain_artifact_rows": [],
        }
    requires_expand = any(_token(target.get("measurement_point_id")) in _INTERNAL_MEASUREMENT_POINTS for target in targets)
    if not requires_expand:
        return {
            "result": "complete",
            "compute_runtime_state": _as_map(_as_map(debug_state).get("compute_runtime_state")),
            "forced_expand_event_rows": [],
            "explain_artifact_rows": [],
        }
    if not bool(allow_force_expand):
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_DEBUG_REQUIRES_EXPAND,
            "compute_runtime_state": _as_map(_as_map(debug_state).get("compute_runtime_state")),
            "forced_expand_event_rows": [],
            "explain_artifact_rows": [
                _debug_explain(
                    explain_kind_id="explain.logic_debug_refused",
                    target_id=network_id,
                    event_id_seed={"network_id": network_id, "reason_code": REFUSAL_LOGIC_DEBUG_REQUIRES_EXPAND},
                    remediation_hints=["attach a permitted analyzer or accept boundary-I/O-only tracing"],
                    extensions={
                        "reason_code": REFUSAL_LOGIC_DEBUG_REQUIRES_EXPAND,
                        "compiled_model_id": _token(compiled_context.get("compiled_model_id")),
                    },
                )
            ],
        }
    expand_compute = request_logic_debug_compute(
        current_tick=current_tick,
        subject_id=network_id,
        phase="forced_expand",
        instruction_units=6,
        memory_units=1,
        compute_runtime_state=_as_map(_as_map(debug_state).get("compute_runtime_state")),
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
        compute_budget_profile_id=_token(compute_budget_profile_id) or "compute.default",
        owner_priority=150,
        critical=False,
    )
    if _token(expand_compute.get("result")) not in {"complete", "throttled"}:
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_DEBUG_REQUIRES_EXPAND,
            "compute_runtime_state": _as_map(expand_compute.get("runtime_state")),
            "forced_expand_event_rows": [],
            "explain_artifact_rows": [
                _debug_explain(
                    explain_kind_id="explain.logic_debug_refused",
                    target_id=network_id,
                    event_id_seed={"network_id": network_id, "phase": "forced_expand"},
                    remediation_hints=["raise compute budget or limit internal debug scope"],
                    extensions={
                        "reason_code": REFUSAL_LOGIC_DEBUG_REQUIRES_EXPAND,
                        "compute_reason_code": _token(expand_compute.get("reason_code")),
                    },
                )
            ],
        }
    forced_expand = build_logic_compiled_forced_expand_event(
        capsule_id=_compiled_capsule_id(network_id),
        tick=int(max(0, _as_int(current_tick, 0))),
        network_id=network_id,
        reason_code="inspection_request",
        compiled_model_id=_token(compiled_context.get("compiled_model_id")),
    )
    return {
        "result": "complete",
        "compute_runtime_state": _as_map(expand_compute.get("runtime_state")),
        "forced_expand_event_rows": [forced_expand] if forced_expand else [],
        "explain_artifact_rows": [
            _debug_explain(
                explain_kind_id="explain.logic_debug_forced_expand",
                target_id=network_id,
                event_id_seed={"network_id": network_id, "compiled_model_id": _token(compiled_context.get("compiled_model_id"))},
                remediation_hints=["capture the internal debug window and release the controller back to compiled mode"],
                extensions={
                    "compiled_model_id": _token(compiled_context.get("compiled_model_id")),
                    "forced_expand_event_id": _token(_as_map(forced_expand).get("event_id")),
                },
            )
        ],
    }


def _trace_target_subset(
    *,
    targets: Sequence[Mapping[str, object]],
    keep_count: int,
    throttle_strategy: str,
    seed_payload: Mapping[str, object],
) -> list[dict]:
    sorted_targets = sorted((dict(row) for row in targets), key=lambda row: _token(row.get("target_key")))
    target_count = len(sorted_targets)
    if keep_count >= target_count:
        return sorted_targets
    if keep_count <= 0:
        return []
    strategy = _token(throttle_strategy) or "deterministic_subsample"
    if strategy == "reduce_points":
        return sorted_targets[:keep_count]
    if strategy == "refuse":
        return []
    ranked = sorted(
        sorted_targets,
        key=lambda row: canonical_sha256(
            {
                "seed": _canon(_as_map(seed_payload)),
                "target_key": _token(row.get("target_key")),
            }
        ),
    )
    return [dict(row) for row in ranked[:keep_count]]


def _sample_target(
    *,
    current_tick: int,
    target: Mapping[str, object],
    signal_store_state: Mapping[str, object] | None,
    logic_network_state: Mapping[str, object] | None,
    logic_eval_state: Mapping[str, object] | None,
    state_vector_snapshot_rows: object,
    compiled_model_rows: object,
    protocol_registry_payload: Mapping[str, object] | None,
    instrumentation_surface_registry_payload: Mapping[str, object] | None,
    access_policy_registry_payload: Mapping[str, object] | None,
    measurement_model_registry_payload: Mapping[str, object] | None,
    authority_context: Mapping[str, object] | None,
    has_physical_access: bool,
    available_instrument_type_ids: object,
) -> dict:
    measurement_point_id = _token(target.get("measurement_point_id"))
    subject_id = _token(target.get("subject_id"))
    network_id = _token(target.get("network_id")) or subject_id
    element_id = _token(target.get("element_id")) or subject_id
    port_id = _token(target.get("port_id"))
    node_id = _token(target.get("node_id"))
    edge_id = _token(target.get("edge_id"))

    if measurement_point_id in {"measure.logic.signal", "measure.logic.bus", "measure.logic.protocol_frame"}:
        signal_row = _select_active_signal_row(
            signal_store_state=signal_store_state,
            network_id=network_id,
            element_id=element_id,
            port_id=port_id,
            tick=current_tick,
        )
        if not signal_row:
            return {"result": "refused", "reason_code": REFUSAL_LOGIC_DEBUG_SUBJECT_NOT_FOUND}
        if measurement_point_id == "measure.logic.bus" and _token(_as_map(signal_row.get("value_ref")).get("value_kind")) != "bus":
            return {"result": "refused", "reason_code": REFUSAL_LOGIC_DEBUG_SUBJECT_NOT_FOUND}
        observation = observe_signal_row(
            signal_row=signal_row,
            current_tick=current_tick,
            authority_context=authority_context,
            has_physical_access=has_physical_access,
            available_instrument_type_ids=available_instrument_type_ids,
            instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
            access_policy_registry_payload=access_policy_registry_payload,
            measurement_model_registry_payload=measurement_model_registry_payload,
            measurement_point_id=measurement_point_id,
        )
        if _token(observation.get("result")) != "complete":
            return dict(observation)
        signal_artifact = dict(observation.get("signal_observation_artifact") or {})
        measurement_artifact = _as_map(_as_map(observation.get("measurement_observation")).get("observation_artifact"))
        sample_value = {
            "measurement_point_id": measurement_point_id,
            "target_key": _sample_target_key(target),
            "measurement_artifact_id": _token(measurement_artifact.get("artifact_id")),
            "observation_artifact_id": _token(signal_artifact.get("artifact_id")),
            "value": measurement_artifact.get("value"),
            "value_hash": canonical_sha256(_canon(signal_artifact)),
        }
        protocol_artifact = {}
        if measurement_point_id == "measure.logic.protocol_frame":
            protocol_artifact = _build_protocol_summary_artifact(
                signal_row=signal_row,
                signal_store_state=signal_store_state,
                protocol_registry_payload=protocol_registry_payload,
                current_tick=current_tick,
            )
            if not protocol_artifact:
                return {"result": "refused", "reason_code": REFUSAL_LOGIC_DEBUG_PROTOCOL_UNAVAILABLE}
            sample_value["protocol_summary_artifact_id"] = _token(protocol_artifact.get("artifact_id"))
            sample_value["value_hash"] = canonical_sha256(_canon(protocol_artifact))
        return {
            "result": "complete",
            "measurement_observation": dict(observation.get("measurement_observation") or {}),
            "observation_artifact_rows": [signal_artifact],
            "protocol_summary_artifact_rows": [protocol_artifact] if protocol_artifact else [],
            "measurement_artifact_id": _token(measurement_artifact.get("artifact_id")),
            "sample_value_row": sample_value,
        }

    if measurement_point_id == "measure.logic.timing_trace":
        return _timing_summary_artifact(
            network_id=network_id,
            current_tick=current_tick,
            logic_eval_state=logic_eval_state,
            authority_context=authority_context,
            has_physical_access=has_physical_access,
            available_instrument_type_ids=available_instrument_type_ids,
            instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
            access_policy_registry_payload=access_policy_registry_payload,
            measurement_model_registry_payload=measurement_model_registry_payload,
        )

    if measurement_point_id == "measure.logic.element.output_port":
        signal_row = _select_active_signal_row(
            signal_store_state=signal_store_state,
            network_id=network_id,
            element_id=element_id,
            port_id=port_id,
            tick=current_tick,
        )
        if not signal_row:
            return {"result": "refused", "reason_code": REFUSAL_LOGIC_DEBUG_SUBJECT_NOT_FOUND}
        observation = observe_logic_element_output_port(
            element_id=element_id,
            raw_value=_measurement_value_for_signal(signal_row),
            current_tick=current_tick,
            authority_context=authority_context,
            has_physical_access=has_physical_access,
            available_instrument_type_ids=available_instrument_type_ids,
            instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
            access_policy_registry_payload=access_policy_registry_payload,
            measurement_model_registry_payload=measurement_model_registry_payload,
        )
        if _token(observation.get("result")) != "complete":
            return dict(observation)
        measurement_artifact = _as_map(observation.get("observation_artifact"))
        artifact = {
            "artifact_id": "artifact.logic.element_output_observation.{}".format(
                canonical_sha256({"element_id": element_id, "port_id": port_id, "tick": int(max(0, _as_int(current_tick, 0)))})[:16]
            ),
            "artifact_family_id": "OBSERVATION",
            "artifact_type_id": "artifact.logic.element_output_observation",
            "element_id": element_id,
            "port_id": port_id,
            "tick": int(max(0, _as_int(current_tick, 0))),
            "measurement_artifact_id": _token(measurement_artifact.get("artifact_id")),
            "deterministic_fingerprint": "",
            "extensions": {
                "signal_id": _token(signal_row.get("signal_id")),
                "signal_hash": canonical_sha256(_canon(signal_row)),
                "trace_compactable": True,
            },
        }
        artifact["deterministic_fingerprint"] = canonical_sha256(dict(artifact, deterministic_fingerprint=""))
        return {
            "result": "complete",
            "measurement_observation": dict(observation),
            "observation_artifact_rows": [artifact],
            "measurement_artifact_id": _token(measurement_artifact.get("artifact_id")),
            "sample_value_row": {
                "measurement_point_id": measurement_point_id,
                "target_key": _sample_target_key(target),
                "measurement_artifact_id": _token(measurement_artifact.get("artifact_id")),
                "observation_artifact_id": _token(artifact.get("artifact_id")),
                "value": measurement_artifact.get("value"),
                "value_hash": canonical_sha256(_canon(artifact)),
            },
        }

    if measurement_point_id == "measure.logic.element.state_vector":
        snapshots = _rows_by_id(state_vector_snapshot_rows, "owner_id")
        snapshot = dict(snapshots.get(element_id) or {})
        if not snapshot:
            return {"result": "refused", "reason_code": REFUSAL_LOGIC_DEBUG_SUBJECT_NOT_FOUND}
        observation = observe_logic_element_state_vector(
            element_id=element_id,
            raw_value=int(canonical_sha256(_canon(_as_map(snapshot.get("serialized_state"))))[:8], 16),
            current_tick=current_tick,
            authority_context=authority_context,
            has_physical_access=has_physical_access,
            available_instrument_type_ids=available_instrument_type_ids,
            instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
            access_policy_registry_payload=access_policy_registry_payload,
            measurement_model_registry_payload=measurement_model_registry_payload,
        )
        if _token(observation.get("result")) != "complete":
            return dict(observation)
        measurement_artifact = _as_map(observation.get("observation_artifact"))
        artifact = {
            "artifact_id": "artifact.logic.state_vector_observation.{}".format(
                canonical_sha256({"owner_id": element_id, "tick": int(max(0, _as_int(current_tick, 0))), "snapshot_id": _token(snapshot.get("snapshot_id"))})[:16]
            ),
            "artifact_family_id": "OBSERVATION",
            "artifact_type_id": "artifact.logic.state_vector_observation",
            "owner_id": element_id,
            "tick": int(max(0, _as_int(current_tick, 0))),
            "measurement_artifact_id": _token(measurement_artifact.get("artifact_id")),
            "deterministic_fingerprint": "",
            "extensions": {
                "snapshot_id": _token(snapshot.get("snapshot_id")),
                "snapshot_hash": canonical_sha256(_canon(snapshot)),
                "trace_compactable": True,
            },
        }
        artifact["deterministic_fingerprint"] = canonical_sha256(dict(artifact, deterministic_fingerprint=""))
        return {
            "result": "complete",
            "measurement_observation": dict(observation),
            "observation_artifact_rows": [artifact],
            "measurement_artifact_id": _token(measurement_artifact.get("artifact_id")),
            "sample_value_row": {
                "measurement_point_id": measurement_point_id,
                "target_key": _sample_target_key(target),
                "measurement_artifact_id": _token(measurement_artifact.get("artifact_id")),
                "observation_artifact_id": _token(artifact.get("artifact_id")),
                "value": measurement_artifact.get("value"),
                "value_hash": canonical_sha256(_canon(artifact)),
            },
        }

    if measurement_point_id in {"measure.logic.network.node", "measure.logic.network.edge", "measure.logic.network.compiled_summary"}:
        binding_row = dict(_logic_binding_by_network_id(logic_network_state).get(network_id) or {})
        graph_row = dict(_logic_graph_by_id(logic_network_state).get(_token(binding_row.get("graph_id"))) or {})
        if measurement_point_id == "measure.logic.network.node":
            node_row = next((dict(item) for item in _as_list(graph_row.get("nodes")) if isinstance(item, Mapping) and _token(item.get("node_id")) == node_id), {})
            if not node_row:
                return {"result": "refused", "reason_code": REFUSAL_LOGIC_DEBUG_SUBJECT_NOT_FOUND}
            observation = observe_logic_network_node(
                network_id=network_id,
                node_row=node_row,
                current_tick=current_tick,
                authority_context=authority_context,
                has_physical_access=has_physical_access,
                available_instrument_type_ids=available_instrument_type_ids,
                instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
                access_policy_registry_payload=access_policy_registry_payload,
                measurement_model_registry_payload=measurement_model_registry_payload,
            )
            if _token(observation.get("result")) != "complete":
                return dict(observation)
            artifact = dict(observation.get("network_node_observation_artifact") or {})
        elif measurement_point_id == "measure.logic.network.edge":
            edge_row = next((dict(item) for item in _as_list(graph_row.get("edges")) if isinstance(item, Mapping) and _token(item.get("edge_id")) == edge_id), {})
            if not edge_row:
                return {"result": "refused", "reason_code": REFUSAL_LOGIC_DEBUG_SUBJECT_NOT_FOUND}
            observation = observe_logic_network_edge(
                network_id=network_id,
                edge_row=edge_row,
                current_tick=current_tick,
                authority_context=authority_context,
                has_physical_access=has_physical_access,
                available_instrument_type_ids=available_instrument_type_ids,
                instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
                access_policy_registry_payload=access_policy_registry_payload,
                measurement_model_registry_payload=measurement_model_registry_payload,
            )
            if _token(observation.get("result")) != "complete":
                return dict(observation)
            artifact = dict(observation.get("network_edge_observation_artifact") or {})
        else:
            compiled_context = _compiled_binding_context(
                logic_network_state=logic_network_state,
                compiled_model_rows=compiled_model_rows,
                network_id=network_id,
            )
            compiled_row = dict(compiled_context.get("compiled_model_row") or {})
            if not compiled_row:
                return {"result": "refused", "reason_code": REFUSAL_LOGIC_DEBUG_SUBJECT_NOT_FOUND}
            observation = observe_logic_network_compiled_summary(
                network_id=network_id,
                compiled_model_row=compiled_row,
                current_tick=current_tick,
                authority_context=authority_context,
                has_physical_access=has_physical_access,
                available_instrument_type_ids=available_instrument_type_ids,
                instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
                access_policy_registry_payload=access_policy_registry_payload,
                measurement_model_registry_payload=measurement_model_registry_payload,
            )
            if _token(observation.get("result")) != "complete":
                return dict(observation)
            artifact = dict(observation.get("compiled_summary_artifact") or {})
            measurement_artifact = _as_map(_as_map(observation.get("measurement_observation")).get("observation_artifact"))
            introspection = build_logic_compiled_introspection_artifact(
                tick=current_tick,
                network_id=network_id,
                compiled_model_row=compiled_row,
                measurement_artifact_id=_token(measurement_artifact.get("artifact_id")),
            )
            return {
                "result": "complete",
                "measurement_observation": dict(observation.get("measurement_observation") or {}),
                "observation_artifact_rows": [artifact],
                "compiled_introspection_artifact_rows": [introspection],
                "measurement_artifact_id": _token(measurement_artifact.get("artifact_id")),
                "sample_value_row": {
                    "measurement_point_id": measurement_point_id,
                    "target_key": _sample_target_key(target),
                    "measurement_artifact_id": _token(measurement_artifact.get("artifact_id")),
                    "observation_artifact_id": _token(artifact.get("artifact_id")),
                    "compiled_introspection_artifact_id": _token(introspection.get("artifact_id")),
                    "value": measurement_artifact.get("value"),
                    "value_hash": canonical_sha256(_canon(introspection)),
                },
            }
        measurement_artifact = _as_map(_as_map(observation.get("measurement_observation")).get("observation_artifact"))
        return {
            "result": "complete",
            "measurement_observation": dict(observation.get("measurement_observation") or {}),
            "observation_artifact_rows": [artifact] if artifact else [],
            "measurement_artifact_id": _token(measurement_artifact.get("artifact_id")),
            "sample_value_row": {
                "measurement_point_id": measurement_point_id,
                "target_key": _sample_target_key(target),
                "measurement_artifact_id": _token(measurement_artifact.get("artifact_id")),
                "observation_artifact_id": _token(artifact.get("artifact_id")),
                "value": measurement_artifact.get("value"),
                "value_hash": canonical_sha256(_canon(artifact)),
            },
        }

    return {"result": "refused", "reason_code": REFUSAL_LOGIC_DEBUG_INVALID_REQUEST}


def process_logic_probe(
    *,
    current_tick: int,
    logic_debug_state: Mapping[str, object] | None,
    signal_store_state: Mapping[str, object] | None,
    logic_network_state: Mapping[str, object] | None,
    logic_eval_state: Mapping[str, object] | None,
    probe_request: Mapping[str, object],
    state_vector_snapshot_rows: object = None,
    compiled_model_rows: object = None,
    protocol_registry_payload: Mapping[str, object] | None = None,
    instrumentation_surface_registry_payload: Mapping[str, object] | None = None,
    access_policy_registry_payload: Mapping[str, object] | None = None,
    measurement_model_registry_payload: Mapping[str, object] | None = None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None = None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None = None,
    compute_budget_profile_id: str = "compute.default",
    authority_context: Mapping[str, object] | None = None,
    has_physical_access: bool = False,
    available_instrument_type_ids: object = None,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    state = normalize_logic_debug_state(logic_debug_state)
    request = _as_map(probe_request)
    request_row = build_logic_debug_probe_request_row(
        request_id=_token(request.get("request_id"))
        or "request.logic.debug_probe.{}".format(canonical_sha256({"tick": tick, "request": _canon(request)})[:16]),
        subject_id=_token(request.get("subject_id")),
        measurement_point_id=_token(request.get("measurement_point_id")),
        tick=int(max(0, _as_int(request.get("tick"), tick))),
        extensions=_as_map(request.get("extensions")),
    )
    if not request_row:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_DEBUG_INVALID_REQUEST, "logic_debug_state": state}
    request_extensions = _as_map(request_row.get("extensions"))
    remote_allowed, remote_reason = _remote_debug_allowed(
        has_physical_access=has_physical_access,
        remote_mode=_token(request_extensions.get("remote_monitoring")) or "sig_authorized_only",
        request_extensions=request_extensions,
    )
    if not remote_allowed:
        explain_rows = normalize_explain_artifact_rows(
            list(state.get("logic_debug_explain_artifact_rows") or [])
            + [
                _debug_explain(
                    explain_kind_id="explain.logic_debug_refused",
                    target_id=_token(request_row.get("subject_id")),
                    event_id_seed={"request_id": _token(request_row.get("request_id"))},
                    remediation_hints=["move within physical access range or provide SIG-mediated remote authorization"],
                    extensions={"reason_code": remote_reason},
                )
            ]
        )
        next_state = normalize_logic_debug_state(
            {
                **state,
                "logic_debug_probe_request_rows": list(state.get("logic_debug_probe_request_rows") or []) + [request_row],
                "logic_debug_explain_artifact_rows": explain_rows,
            }
        )
        return {
            "result": "refused",
            "reason_code": remote_reason,
            "logic_debug_state": next_state,
            "explain_artifact_rows": explain_rows,
        }

    target = dict(request_extensions)
    target["measurement_point_id"] = _token(request_row.get("measurement_point_id"))
    target["subject_id"] = _token(request_row.get("subject_id"))
    target["target_key"] = _sample_target_key(target)

    compiled_access = _prepare_compiled_debug_access(
        current_tick=tick,
        network_id=_token(target.get("network_id")) or _token(request_row.get("subject_id")),
        targets=[target],
        allow_force_expand=bool(request_extensions.get("allow_force_expand", False)),
        debug_state=state,
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
        compute_budget_profile_id=_token(request_extensions.get("compute_profile_id")) or _token(compute_budget_profile_id) or "compute.default",
        logic_network_state=logic_network_state,
        compiled_model_rows=compiled_model_rows,
    )
    if _token(compiled_access.get("result")) != "complete":
        next_state = normalize_logic_debug_state(
            {
                **state,
                "logic_debug_probe_request_rows": list(state.get("logic_debug_probe_request_rows") or []) + [request_row],
                "logic_debug_explain_artifact_rows": list(state.get("logic_debug_explain_artifact_rows") or [])
                + [dict(row) for row in _as_list(compiled_access.get("explain_artifact_rows")) if isinstance(row, Mapping)],
                "compute_runtime_state": _as_map(compiled_access.get("compute_runtime_state")),
            }
        )
        return {
            "result": "refused",
            "reason_code": _token(compiled_access.get("reason_code")) or REFUSAL_LOGIC_DEBUG_REQUIRES_EXPAND,
            "logic_debug_state": next_state,
            "forced_expand_event_rows": list(compiled_access.get("forced_expand_event_rows") or []),
            "explain_artifact_rows": list(next_state.get("logic_debug_explain_artifact_rows") or []),
        }
    compute_request = request_logic_debug_compute(
        current_tick=tick,
        subject_id=_token(request_row.get("subject_id")),
        phase="probe",
        instruction_units=8,
        memory_units=2,
        compute_runtime_state=_as_map(compiled_access.get("compute_runtime_state")),
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
        compute_budget_profile_id=_token(request_extensions.get("compute_profile_id")) or _token(compute_budget_profile_id) or "compute.default",
        owner_priority=145,
        critical=False,
    )
    if _token(compute_request.get("result")) not in {"complete", "throttled"}:
        explain = _debug_explain(
            explain_kind_id="explain.logic_debug_throttled",
            target_id=_token(request_row.get("subject_id")),
            event_id_seed={"request_id": _token(request_row.get("request_id")), "phase": "probe"},
            remediation_hints=["reduce debug load or raise debug compute budget"],
            extensions={"reason_code": _token(compute_request.get("reason_code")), "phase": "probe"},
        )
        next_state = normalize_logic_debug_state(
            {
                **state,
                "logic_debug_probe_request_rows": list(state.get("logic_debug_probe_request_rows") or []) + [request_row],
                "logic_debug_explain_artifact_rows": list(state.get("logic_debug_explain_artifact_rows") or []) + [explain],
                "compute_runtime_state": _as_map(compute_request.get("runtime_state")),
            }
        )
        return {
            "result": "refused",
            "reason_code": _token(compute_request.get("reason_code")) or REFUSAL_LOGIC_DEBUG_ACCESS_DENIED,
            "logic_debug_state": next_state,
            "forced_expand_event_rows": list(compiled_access.get("forced_expand_event_rows") or []),
            "explain_artifact_rows": list(next_state.get("logic_debug_explain_artifact_rows") or []),
        }
    sample = _sample_target(
        current_tick=tick,
        target=target,
        signal_store_state=signal_store_state,
        logic_network_state=logic_network_state,
        logic_eval_state=logic_eval_state,
        state_vector_snapshot_rows=state_vector_snapshot_rows,
        compiled_model_rows=compiled_model_rows,
        protocol_registry_payload=protocol_registry_payload,
        instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
        access_policy_registry_payload=access_policy_registry_payload,
        measurement_model_registry_payload=measurement_model_registry_payload,
        authority_context=authority_context,
        has_physical_access=has_physical_access,
        available_instrument_type_ids=available_instrument_type_ids,
    )
    if _token(sample.get("result")) != "complete":
        explain = _debug_explain(
            explain_kind_id="explain.logic_debug_refused",
            target_id=_token(request_row.get("subject_id")),
            event_id_seed={"request_id": _token(request_row.get("request_id")), "measurement_point_id": _token(request_row.get("measurement_point_id"))},
            remediation_hints=["verify target identity, access policy, and instrument type"],
            extensions={"reason_code": _token(sample.get("reason_code"))},
        )
        next_state = normalize_logic_debug_state(
            {
                **state,
                "logic_debug_probe_request_rows": list(state.get("logic_debug_probe_request_rows") or []) + [request_row],
                "logic_debug_explain_artifact_rows": list(state.get("logic_debug_explain_artifact_rows") or [])
                + [dict(row) for row in _as_list(compiled_access.get("explain_artifact_rows")) if isinstance(row, Mapping)]
                + [explain],
                "compute_runtime_state": _as_map(compute_request.get("runtime_state")),
            }
        )
        return {
            "result": "refused",
            "reason_code": _token(sample.get("reason_code")) or REFUSAL_LOGIC_DEBUG_SUBJECT_NOT_FOUND,
            "logic_debug_state": next_state,
            "forced_expand_event_rows": list(compiled_access.get("forced_expand_event_rows") or []),
            "explain_artifact_rows": list(next_state.get("logic_debug_explain_artifact_rows") or []),
        }
    measurement_observation = dict(sample.get("measurement_observation") or {})
    measurement_artifact_id = _token(sample.get("measurement_artifact_id"))
    probe_artifact = _probe_artifact(
        request_row=request_row,
        current_tick=tick,
        measurement_artifact_id=measurement_artifact_id,
        sample_value_row=_as_map(sample.get("sample_value_row")),
    )
    explain_rows = list(compiled_access.get("explain_artifact_rows") or [])
    if _token(compute_request.get("result")) == "throttled":
        explain_rows.append(
            _debug_explain(
                explain_kind_id="explain.logic_debug_throttled",
                target_id=_token(request_row.get("subject_id")),
                event_id_seed={"request_id": _token(request_row.get("request_id")), "phase": "probe", "throttled": True},
                remediation_hints=["lower concurrent debug load or widen the compute profile"],
                extensions={"phase": "probe", "reason_code": _token(compute_request.get("reason_code"))},
            )
        )
    next_state = normalize_logic_debug_state(
        {
            **state,
            "logic_debug_probe_request_rows": list(state.get("logic_debug_probe_request_rows") or []) + [request_row],
            "logic_debug_probe_artifact_rows": list(state.get("logic_debug_probe_artifact_rows") or []) + [probe_artifact],
            "logic_protocol_summary_artifact_rows": list(state.get("logic_protocol_summary_artifact_rows") or [])
            + [dict(row) for row in _as_list(sample.get("protocol_summary_artifact_rows")) if isinstance(row, Mapping)],
            "logic_debug_explain_artifact_rows": list(state.get("logic_debug_explain_artifact_rows") or [])
            + [dict(row) for row in explain_rows if isinstance(row, Mapping)],
            "compute_runtime_state": _as_map(compute_request.get("runtime_state")),
        }
    )
    return {
        "result": "complete" if _token(compute_request.get("result")) == "complete" else "throttled",
        "reason_code": _token(compute_request.get("reason_code")),
        "logic_debug_state": next_state,
        "measurement_observation": measurement_observation,
        "probe_artifact_row": probe_artifact,
        "probe_artifact_rows": [probe_artifact],
        "observation_artifact_rows": [dict(row) for row in _as_list(sample.get("observation_artifact_rows")) if isinstance(row, Mapping)],
        "protocol_summary_artifact_rows": [dict(row) for row in _as_list(sample.get("protocol_summary_artifact_rows")) if isinstance(row, Mapping)],
        "compiled_introspection_artifact_rows": [dict(row) for row in _as_list(sample.get("compiled_introspection_artifact_rows")) if isinstance(row, Mapping)],
        "forced_expand_event_rows": list(compiled_access.get("forced_expand_event_rows") or []),
        "explain_artifact_rows": [dict(row) for row in list(next_state.get("logic_debug_explain_artifact_rows") or []) if isinstance(row, Mapping)],
    }


def process_logic_trace_start(
    *,
    current_tick: int,
    logic_debug_state: Mapping[str, object] | None,
    logic_network_state: Mapping[str, object] | None,
    trace_request: Mapping[str, object],
    compiled_model_rows: object = None,
    debug_sampling_policy_registry_payload: Mapping[str, object] | None = None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None = None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None = None,
    compute_budget_profile_id: str = "compute.default",
    has_physical_access: bool = False,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    state = normalize_logic_debug_state(logic_debug_state)
    request = _as_map(trace_request)
    request_row = build_logic_debug_trace_request_row(
        request_id=_token(request.get("request_id"))
        or "request.logic.trace.{}".format(canonical_sha256({"tick": tick, "request": _canon(request)})[:16]),
        subject_id=_token(request.get("subject_id")),
        measurement_point_ids=_as_list(request.get("measurement_point_ids")),
        tick_start=_as_int(request.get("tick_start"), tick),
        tick_end=_as_int(request.get("tick_end"), tick),
        sampling_policy_id=_token(request.get("sampling_policy_id")) or "debug.sample.default",
        extensions=_as_map(request.get("extensions")),
    )
    if not request_row:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_DEBUG_INVALID_REQUEST, "logic_debug_state": state}
    policy_rows = _debug_sampling_policy_rows_by_id(debug_sampling_policy_registry_payload)
    policy_row = dict(policy_rows.get(_token(request_row.get("sampling_policy_id"))) or {})
    if not policy_row:
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_DEBUG_SAMPLING_POLICY_UNREGISTERED,
            "logic_debug_state": state,
        }
    targets = _targets_from_trace_request(request_row)
    extensions = _as_map(request_row.get("extensions"))
    remote_allowed, remote_reason = _remote_debug_allowed(
        has_physical_access=has_physical_access,
        remote_mode=_token(_as_map(policy_row.get("extensions")).get("remote_monitoring")) or "sig_authorized_only",
        request_extensions=extensions,
    )
    if not remote_allowed:
        explain = _debug_explain(
            explain_kind_id="explain.logic_debug_refused",
            target_id=_token(request_row.get("subject_id")),
            event_id_seed={"request_id": _token(request_row.get("request_id")), "reason": remote_reason},
            remediation_hints=["move within physical access range or provide a SIG-mediated remote authorization receipt"],
            extensions={"reason_code": remote_reason},
        )
        next_state = normalize_logic_debug_state(
            {
                **state,
                "logic_debug_trace_request_rows": list(state.get("logic_debug_trace_request_rows") or []) + [request_row],
                "logic_debug_explain_artifact_rows": list(state.get("logic_debug_explain_artifact_rows") or []) + [explain],
            }
        )
        return {
            "result": "refused",
            "reason_code": remote_reason,
            "logic_debug_state": next_state,
            "explain_artifact_rows": [explain],
        }
    tick_span = int(max(1, _as_int(request_row.get("tick_end"), tick) - _as_int(request_row.get("tick_start"), tick) + 1))
    max_points = int(max(1, _as_int(policy_row.get("max_points"), 1)))
    max_ticks = int(max(1, _as_int(policy_row.get("max_ticks"), 1)))
    max_samples = int(max(1, _as_int(policy_row.get("max_samples"), 1)))
    estimated_samples = int(len(targets) * tick_span)
    if len(targets) > max_points or tick_span > max_ticks or estimated_samples > max_samples:
        explain = _debug_explain(
            explain_kind_id="explain.logic_debug_refused",
            target_id=_token(request_row.get("subject_id")),
            event_id_seed={"request_id": _token(request_row.get("request_id")), "reason": REFUSAL_LOGIC_DEBUG_TRACE_BOUNDS_EXCEEDED},
            remediation_hints=["reduce the trace point count, tick window, or total requested samples"],
            extensions={
                "reason_code": REFUSAL_LOGIC_DEBUG_TRACE_BOUNDS_EXCEEDED,
                "requested_points": len(targets),
                "requested_ticks": tick_span,
                "requested_samples": estimated_samples,
                "max_points": max_points,
                "max_ticks": max_ticks,
                "max_samples": max_samples,
            },
        )
        next_state = normalize_logic_debug_state(
            {
                **state,
                "logic_debug_trace_request_rows": list(state.get("logic_debug_trace_request_rows") or []) + [request_row],
                "logic_debug_explain_artifact_rows": list(state.get("logic_debug_explain_artifact_rows") or []) + [explain],
            }
        )
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_DEBUG_TRACE_BOUNDS_EXCEEDED,
            "logic_debug_state": next_state,
            "explain_artifact_rows": [explain],
        }
    compiled_access = _prepare_compiled_debug_access(
        current_tick=tick,
        network_id=_token(extensions.get("network_id")) or _token(request_row.get("subject_id")),
        targets=targets,
        allow_force_expand=bool(_as_map(policy_row.get("extensions")).get("allow_force_expand", False)),
        debug_state=state,
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
        compute_budget_profile_id=_token(request.get("compute_profile_id")) or _token(compute_budget_profile_id) or "compute.default",
        logic_network_state=logic_network_state,
        compiled_model_rows=compiled_model_rows,
    )
    if _token(compiled_access.get("result")) != "complete":
        next_state = normalize_logic_debug_state(
            {
                **state,
                "logic_debug_trace_request_rows": list(state.get("logic_debug_trace_request_rows") or []) + [request_row],
                "logic_debug_explain_artifact_rows": list(state.get("logic_debug_explain_artifact_rows") or [])
                + [dict(row) for row in _as_list(compiled_access.get("explain_artifact_rows")) if isinstance(row, Mapping)],
                "compute_runtime_state": _as_map(compiled_access.get("compute_runtime_state")),
            }
        )
        return {
            "result": "refused",
            "reason_code": _token(compiled_access.get("reason_code")) or REFUSAL_LOGIC_DEBUG_REQUIRES_EXPAND,
            "logic_debug_state": next_state,
            "forced_expand_event_rows": list(compiled_access.get("forced_expand_event_rows") or []),
            "explain_artifact_rows": list(next_state.get("logic_debug_explain_artifact_rows") or []),
        }
    compute_request = request_logic_debug_compute(
        current_tick=tick,
        subject_id=_token(request_row.get("subject_id")),
        phase="trace.start",
        instruction_units=max(4, len(targets) * 2),
        memory_units=max(1, len(targets)),
        compute_runtime_state=_as_map(compiled_access.get("compute_runtime_state")),
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
        compute_budget_profile_id=_token(request.get("compute_profile_id")) or _token(compute_budget_profile_id) or "compute.default",
        owner_priority=142,
        critical=False,
    )
    if _token(compute_request.get("result")) not in {"complete", "throttled"}:
        explain = _debug_explain(
            explain_kind_id="explain.logic_debug_throttled",
            target_id=_token(request_row.get("subject_id")),
            event_id_seed={"request_id": _token(request_row.get("request_id")), "phase": "trace.start"},
            remediation_hints=["reduce concurrent trace sessions or raise trace compute budget"],
            extensions={"reason_code": _token(compute_request.get("reason_code")), "phase": "trace.start"},
        )
        next_state = normalize_logic_debug_state(
            {
                **state,
                "logic_debug_trace_request_rows": list(state.get("logic_debug_trace_request_rows") or []) + [request_row],
                "logic_debug_explain_artifact_rows": list(state.get("logic_debug_explain_artifact_rows") or [])
                + [dict(row) for row in _as_list(compiled_access.get("explain_artifact_rows")) if isinstance(row, Mapping)]
                + [explain],
                "compute_runtime_state": _as_map(compute_request.get("runtime_state")),
            }
        )
        return {
            "result": "refused",
            "reason_code": _token(compute_request.get("reason_code")) or REFUSAL_LOGIC_DEBUG_ACCESS_DENIED,
            "logic_debug_state": next_state,
            "forced_expand_event_rows": list(compiled_access.get("forced_expand_event_rows") or []),
            "explain_artifact_rows": list(next_state.get("logic_debug_explain_artifact_rows") or []),
        }
    session_row = build_logic_debug_trace_session_row(
        session_id="session.logic.trace.{}".format(canonical_sha256({"request_id": _token(request_row.get("request_id"))})[:16]),
        request_id=_token(request_row.get("request_id")),
        subject_id=_token(request_row.get("subject_id")),
        measurement_point_ids=_as_list(request_row.get("measurement_point_ids")),
        tick_start=_as_int(request_row.get("tick_start"), tick),
        tick_end=_as_int(request_row.get("tick_end"), tick),
        sampling_policy_id=_token(request_row.get("sampling_policy_id")),
        status="active",
        max_samples=max_samples,
        sample_rows=[],
        sample_count=0,
        extensions={
            "targets": targets,
            "throttle_strategy": _token(policy_row.get("throttle_strategy")) or "deterministic_subsample",
            "record_class": _token(_as_map(policy_row.get("extensions")).get("request_record_class")) or "derived",
            "allow_force_expand": bool(_as_map(policy_row.get("extensions")).get("allow_force_expand", False)),
            "trace_compactable": True,
        },
    )
    explain_rows = list(compiled_access.get("explain_artifact_rows") or [])
    if _token(compute_request.get("result")) == "throttled":
        explain_rows.append(
            _debug_explain(
                explain_kind_id="explain.logic_debug_throttled",
                target_id=_token(request_row.get("subject_id")),
                event_id_seed={"request_id": _token(request_row.get("request_id")), "phase": "trace.start", "throttled": True},
                remediation_hints=["accept reduced trace capacity or select a narrower capture scope"],
                extensions={"phase": "trace.start", "reason_code": _token(compute_request.get("reason_code"))},
            )
        )
    next_state = normalize_logic_debug_state(
        {
            **state,
            "logic_debug_trace_request_rows": list(state.get("logic_debug_trace_request_rows") or []) + [request_row],
            "logic_debug_trace_session_rows": list(state.get("logic_debug_trace_session_rows") or []) + [session_row],
            "logic_debug_explain_artifact_rows": list(state.get("logic_debug_explain_artifact_rows") or [])
            + [dict(row) for row in explain_rows if isinstance(row, Mapping)],
            "compute_runtime_state": _as_map(compute_request.get("runtime_state")),
        }
    )
    return {
        "result": "complete" if _token(compute_request.get("result")) == "complete" else "throttled",
        "reason_code": _token(compute_request.get("reason_code")),
        "logic_debug_state": next_state,
        "trace_request_row": request_row,
        "trace_session_row": session_row,
        "forced_expand_event_rows": list(compiled_access.get("forced_expand_event_rows") or []),
        "explain_artifact_rows": [dict(row) for row in list(next_state.get("logic_debug_explain_artifact_rows") or []) if isinstance(row, Mapping)],
    }


def process_logic_trace_tick(
    *,
    current_tick: int,
    logic_debug_state: Mapping[str, object] | None,
    signal_store_state: Mapping[str, object] | None,
    logic_network_state: Mapping[str, object] | None,
    logic_eval_state: Mapping[str, object] | None,
    trace_tick_request: Mapping[str, object],
    state_vector_snapshot_rows: object = None,
    compiled_model_rows: object = None,
    protocol_registry_payload: Mapping[str, object] | None = None,
    instrumentation_surface_registry_payload: Mapping[str, object] | None = None,
    access_policy_registry_payload: Mapping[str, object] | None = None,
    measurement_model_registry_payload: Mapping[str, object] | None = None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None = None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None = None,
    compute_budget_profile_id: str = "compute.default",
    authority_context: Mapping[str, object] | None = None,
    has_physical_access: bool = False,
    available_instrument_type_ids: object = None,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    state = normalize_logic_debug_state(logic_debug_state)
    request = _as_map(trace_tick_request)
    session_id = _token(request.get("session_id"))
    sessions = _rows_by_id(state.get("logic_debug_trace_session_rows"), "session_id")
    session_row = dict(sessions.get(session_id) or {})
    if not session_row:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_DEBUG_TRACE_SESSION_NOT_FOUND, "logic_debug_state": state}
    if _token(session_row.get("status")) not in {"active", "throttled"}:
        return {"result": "complete", "reason_code": "", "logic_debug_state": state, "trace_session_row": session_row}
    if tick < _as_int(session_row.get("tick_start"), tick) or tick > _as_int(session_row.get("tick_end"), tick):
        return {"result": "complete", "reason_code": "", "logic_debug_state": state, "trace_session_row": session_row}
    targets = [dict(item) for item in _as_list(_as_map(session_row.get("extensions")).get("targets")) if isinstance(item, Mapping)]
    requested_points = int(len(targets))
    compute_request = request_logic_debug_compute(
        current_tick=tick,
        subject_id=_token(session_row.get("subject_id")),
        phase="trace.tick",
        instruction_units=max(2, requested_points * 3),
        memory_units=max(1, requested_points),
        compute_runtime_state=_as_map(state.get("compute_runtime_state")),
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
        compute_budget_profile_id=_token(request.get("compute_profile_id")) or _token(compute_budget_profile_id) or "compute.default",
        owner_priority=141,
        critical=False,
    )
    sample_rows = [dict(row) for row in _as_list(session_row.get("sample_rows")) if isinstance(row, Mapping)]
    sample_count = int(max(0, _as_int(session_row.get("sample_count"), 0)))
    max_samples = int(max(1, _as_int(session_row.get("max_samples"), 1)))
    throttle_strategy = _token(_as_map(session_row.get("extensions")).get("throttle_strategy")) or "deterministic_subsample"
    explain_rows = []
    if _token(compute_request.get("result")) not in {"complete", "throttled"}:
        explain_rows.append(
            _debug_explain(
                explain_kind_id="explain.logic_debug_throttled",
                target_id=_token(session_row.get("subject_id")),
                event_id_seed={"session_id": session_id, "tick": tick, "phase": "trace.tick"},
                remediation_hints=["reduce concurrent trace work or shorten the active trace window"],
                extensions={"phase": "trace.tick", "reason_code": _token(compute_request.get("reason_code"))},
            )
        )
        sessions[session_id] = build_logic_debug_trace_session_row(
            session_id=_token(session_row.get("session_id")),
            request_id=_token(session_row.get("request_id")),
            subject_id=_token(session_row.get("subject_id")),
            measurement_point_ids=_as_list(session_row.get("measurement_point_ids")),
            tick_start=_as_int(session_row.get("tick_start"), tick),
            tick_end=_as_int(session_row.get("tick_end"), tick),
            sampling_policy_id=_token(session_row.get("sampling_policy_id")),
            status="throttled",
            max_samples=max_samples,
            sample_rows=sample_rows,
            sample_count=sample_count,
            extensions=_as_map(session_row.get("extensions")),
        )
        next_state = normalize_logic_debug_state(
            {
                **state,
                "logic_debug_trace_session_rows": list(sessions.values()),
                "logic_debug_explain_artifact_rows": list(state.get("logic_debug_explain_artifact_rows") or []) + explain_rows,
                "compute_runtime_state": _as_map(compute_request.get("runtime_state")),
            }
        )
        return {
            "result": "throttled",
            "reason_code": _token(compute_request.get("reason_code")),
            "logic_debug_state": next_state,
            "trace_session_row": sessions[session_id],
            "explain_artifact_rows": explain_rows,
            "trace_artifact_rows": [],
        }
    keep_count = requested_points
    if _token(compute_request.get("result")) == "throttled":
        keep_count = int(max(0, min(requested_points, _as_int(compute_request.get("approved_instruction_units"), 0) // 3)))
        keep_count = max(1, keep_count) if throttle_strategy != "refuse" else 0
    selected_targets = _trace_target_subset(
        targets=targets,
        keep_count=keep_count,
        throttle_strategy=throttle_strategy,
        seed_payload={"session_id": session_id, "tick": tick},
    )
    if not selected_targets and throttle_strategy == "refuse":
        explain_rows.append(
            _debug_explain(
                explain_kind_id="explain.logic_debug_throttled",
                target_id=_token(session_row.get("subject_id")),
                event_id_seed={"session_id": session_id, "tick": tick, "strategy": "refuse"},
                remediation_hints=["switch to a less expensive sampling policy or reduce sampled points"],
                extensions={"phase": "trace.tick", "reason_code": _token(compute_request.get("reason_code")), "throttle_strategy": "refuse"},
            )
        )
    value_budget = int(max(0, max_samples - sample_count))
    observation_artifact_rows = []
    protocol_summary_artifact_rows = []
    compiled_introspection_artifact_rows = []
    sample_values = []
    for target in selected_targets:
        if value_budget <= 0:
            break
        sampled = _sample_target(
            current_tick=tick,
            target=target,
            signal_store_state=signal_store_state,
            logic_network_state=logic_network_state,
            logic_eval_state=logic_eval_state,
            state_vector_snapshot_rows=state_vector_snapshot_rows,
            compiled_model_rows=compiled_model_rows,
            protocol_registry_payload=protocol_registry_payload,
            instrumentation_surface_registry_payload=instrumentation_surface_registry_payload,
            access_policy_registry_payload=access_policy_registry_payload,
            measurement_model_registry_payload=measurement_model_registry_payload,
            authority_context=authority_context,
            has_physical_access=has_physical_access,
            available_instrument_type_ids=available_instrument_type_ids,
        )
        if _token(sampled.get("result")) != "complete":
            explain_rows.append(
                _debug_explain(
                    explain_kind_id="explain.logic_debug_refused",
                    target_id=_token(session_row.get("subject_id")),
                    event_id_seed={"session_id": session_id, "tick": tick, "target_key": _token(target.get("target_key"))},
                    remediation_hints=["verify target identity and active instrumentation access"],
                    extensions={"reason_code": _token(sampled.get("reason_code"))},
                )
            )
            continue
        sample_values.append(_canon(_as_map(sampled.get("sample_value_row"))))
        observation_artifact_rows.extend(dict(row) for row in _as_list(sampled.get("observation_artifact_rows")) if isinstance(row, Mapping))
        protocol_summary_artifact_rows.extend(dict(row) for row in _as_list(sampled.get("protocol_summary_artifact_rows")) if isinstance(row, Mapping))
        compiled_introspection_artifact_rows.extend(dict(row) for row in _as_list(sampled.get("compiled_introspection_artifact_rows")) if isinstance(row, Mapping))
        value_budget -= 1
    if (_token(compute_request.get("result")) == "throttled") and (len(selected_targets) < requested_points):
        explain_rows.append(
            _debug_explain(
                explain_kind_id="explain.logic_debug_throttled",
                target_id=_token(session_row.get("subject_id")),
                event_id_seed={"session_id": session_id, "tick": tick, "selected_targets": len(selected_targets)},
                remediation_hints=["accept deterministic subsampling or choose a narrower target set"],
                extensions={
                    "phase": "trace.tick",
                    "requested_points": requested_points,
                    "sampled_points": len(selected_targets),
                    "throttle_strategy": throttle_strategy,
                },
            )
        )
    segment_artifact_rows = []
    if sample_values:
        sample_row = {"tick": tick, "values": sample_values}
        sample_rows = sample_rows + [sample_row]
        sample_count += len(sample_values)
        segment_artifact = build_logic_debug_trace_artifact_row(
            trace_id="trace.logic.segment.{}".format(canonical_sha256({"session_id": session_id, "tick": tick, "values": sample_values})[:16]),
            request_id=_token(session_row.get("request_id")),
            samples=[sample_row],
            extensions={"artifact_role": "segment", "session_id": session_id, "trace_compactable": True},
        )
        segment_artifact_rows.append(segment_artifact)
    status = "complete" if tick >= _as_int(session_row.get("tick_end"), tick) or sample_count >= max_samples else "active"
    sessions[session_id] = build_logic_debug_trace_session_row(
        session_id=_token(session_row.get("session_id")),
        request_id=_token(session_row.get("request_id")),
        subject_id=_token(session_row.get("subject_id")),
        measurement_point_ids=_as_list(session_row.get("measurement_point_ids")),
        tick_start=_as_int(session_row.get("tick_start"), tick),
        tick_end=_as_int(session_row.get("tick_end"), tick),
        sampling_policy_id=_token(session_row.get("sampling_policy_id")),
        status=status,
        max_samples=max_samples,
        sample_rows=sample_rows,
        sample_count=sample_count,
        extensions=_as_map(session_row.get("extensions")),
    )
    next_state = normalize_logic_debug_state(
        {
            **state,
            "logic_debug_trace_session_rows": list(sessions.values()),
            "logic_debug_trace_artifact_rows": list(state.get("logic_debug_trace_artifact_rows") or []) + segment_artifact_rows,
            "logic_protocol_summary_artifact_rows": list(state.get("logic_protocol_summary_artifact_rows") or []) + protocol_summary_artifact_rows,
            "logic_debug_explain_artifact_rows": list(state.get("logic_debug_explain_artifact_rows") or []) + explain_rows,
            "compute_runtime_state": _as_map(compute_request.get("runtime_state")),
        }
    )
    return {
        "result": "complete" if _token(compute_request.get("result")) == "complete" else "throttled",
        "reason_code": _token(compute_request.get("reason_code")),
        "logic_debug_state": next_state,
        "trace_session_row": sessions[session_id],
        "trace_artifact_rows": segment_artifact_rows,
        "observation_artifact_rows": observation_artifact_rows,
        "protocol_summary_artifact_rows": protocol_summary_artifact_rows,
        "compiled_introspection_artifact_rows": compiled_introspection_artifact_rows,
        "explain_artifact_rows": explain_rows,
    }


def process_logic_trace_end(
    *,
    current_tick: int,
    logic_debug_state: Mapping[str, object] | None,
    trace_end_request: Mapping[str, object],
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    state = normalize_logic_debug_state(logic_debug_state)
    request = _as_map(trace_end_request)
    session_id = _token(request.get("session_id"))
    sessions = _rows_by_id(state.get("logic_debug_trace_session_rows"), "session_id")
    session_row = dict(sessions.get(session_id) or {})
    if not session_row:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_DEBUG_TRACE_SESSION_NOT_FOUND, "logic_debug_state": state}
    final_artifact = build_logic_debug_trace_artifact_row(
        trace_id="trace.logic.final.{}".format(canonical_sha256({"session_id": session_id, "tick": tick})[:16]),
        request_id=_token(session_row.get("request_id")),
        samples=_as_list(session_row.get("sample_rows")),
        extensions={"artifact_role": "final", "session_id": session_id, "trace_compactable": True},
    )
    sessions[session_id] = build_logic_debug_trace_session_row(
        session_id=_token(session_row.get("session_id")),
        request_id=_token(session_row.get("request_id")),
        subject_id=_token(session_row.get("subject_id")),
        measurement_point_ids=_as_list(session_row.get("measurement_point_ids")),
        tick_start=_as_int(session_row.get("tick_start"), tick),
        tick_end=_as_int(session_row.get("tick_end"), tick),
        sampling_policy_id=_token(session_row.get("sampling_policy_id")),
        status="complete",
        max_samples=_as_int(session_row.get("max_samples"), 1),
        sample_rows=_as_list(session_row.get("sample_rows")),
        sample_count=_as_int(session_row.get("sample_count"), 0),
        extensions=_as_map(session_row.get("extensions")),
    )
    next_state = normalize_logic_debug_state(
        {
            **state,
            "logic_debug_trace_session_rows": list(sessions.values()),
            "logic_debug_trace_artifact_rows": list(state.get("logic_debug_trace_artifact_rows") or []) + [final_artifact],
        }
    )
    return {
        "result": "complete",
        "reason_code": "",
        "logic_debug_state": next_state,
        "trace_session_row": sessions[session_id],
        "trace_artifact_row": final_artifact,
        "trace_artifact_rows": [final_artifact],
    }


__all__ = [
    "PROCESS_LOGIC_PROBE",
    "PROCESS_LOGIC_TRACE_END",
    "PROCESS_LOGIC_TRACE_START",
    "PROCESS_LOGIC_TRACE_TICK",
    "REFUSAL_LOGIC_DEBUG_ACCESS_DENIED",
    "REFUSAL_LOGIC_DEBUG_INVALID_REQUEST",
    "REFUSAL_LOGIC_DEBUG_PROTOCOL_UNAVAILABLE",
    "REFUSAL_LOGIC_DEBUG_REQUIRES_EXPAND",
    "REFUSAL_LOGIC_DEBUG_SAMPLING_POLICY_UNREGISTERED",
    "REFUSAL_LOGIC_DEBUG_SUBJECT_NOT_FOUND",
    "REFUSAL_LOGIC_DEBUG_TRACE_BOUNDS_EXCEEDED",
    "REFUSAL_LOGIC_DEBUG_TRACE_SESSION_NOT_FOUND",
    "process_logic_probe",
    "process_logic_trace_end",
    "process_logic_trace_start",
    "process_logic_trace_tick",
]
