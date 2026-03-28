"""Deterministic EMB-1 logic probe and analyzer tool planners."""

from __future__ import annotations

from typing import Mapping

from compat import REFUSAL_COMPAT_FEATURE_DISABLED, enforce_negotiated_capability
from tools.xstack.compatx.canonical_json import canonical_sha256

from .toolbelt_engine import evaluate_tool_access, tool_capability_rows_by_id


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _refusal(code: str, message: str, details: Mapping[str, object] | None = None) -> dict:
    payload = {
        "result": "refused",
        "reason_code": str(code or "").strip(),
        "message": str(message or "").strip(),
        "details": _as_map(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_logic_probe_task(
    *,
    authority_context: Mapping[str, object] | None,
    compat_runtime_state: Mapping[str, object] | None = None,
    subject_id: str,
    measurement_point_id: str,
    network_id: str,
    element_id: str,
    port_id: str,
) -> dict:
    compat_result = enforce_negotiated_capability(
        compat_runtime_state,
        capability_id="cap.logic.protocol_layer",
        action_label="logic_probe",
    )
    # "refusal.compat.feature_disabled" is the explicit CAP-NEG-3 refusal for negotiated disables.
    if str(compat_result.get("reason_code", "")).strip() == REFUSAL_COMPAT_FEATURE_DISABLED:
        return dict(compat_result)
    if str(compat_result.get("result", "")).strip() != "complete":
        return dict(compat_result)
    access_result = evaluate_tool_access(tool_id="tool.logic_probe", authority_context=authority_context, has_physical_access=True)
    if str(access_result.get("result", "")).strip() != "complete":
        return dict(access_result)
    if not str(measurement_point_id or "").strip():
        return _refusal("refusal.tool.measurement_point_missing", "logic probe requires a measurement_point_id")
    probe_request = {
        "request_id": "request.logic_probe.{}".format(
            canonical_sha256(
                {
                    "subject_id": str(subject_id or "").strip(),
                    "measurement_point_id": str(measurement_point_id or "").strip(),
                    "network_id": str(network_id or "").strip(),
                    "element_id": str(element_id or "").strip(),
                    "port_id": str(port_id or "").strip(),
                }
            )[:16]
        ),
        "subject_id": str(subject_id or "").strip(),
        "measurement_point_id": str(measurement_point_id or "").strip(),
        "extensions": {
            "network_id": str(network_id or "").strip(),
            "element_id": str(element_id or "").strip(),
            "port_id": str(port_id or "").strip(),
            "source": "EMB1-5",
        },
    }
    payload = {
        "result": "complete",
        "tool_id": "tool.logic_probe",
        "probe_request": dict(probe_request),
        "process_sequence": [{"process_id": "process.logic_probe", "inputs": {"probe_request": dict(probe_request)}}],
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_logic_trace_task(
    *,
    authority_context: Mapping[str, object] | None,
    compat_runtime_state: Mapping[str, object] | None = None,
    subject_id: str,
    measurement_point_ids: object,
    targets: object,
    current_tick: int,
    duration_ticks: int,
    sampling_policy_id: str = "debug.sample.default",
) -> dict:
    compat_result = enforce_negotiated_capability(
        compat_runtime_state,
        capability_id="cap.logic.debug_analyzer",
        action_label="logic_trace",
    )
    # "refusal.compat.feature_disabled" is the explicit CAP-NEG-3 refusal for negotiated disables.
    if str(compat_result.get("reason_code", "")).strip() == REFUSAL_COMPAT_FEATURE_DISABLED:
        return dict(compat_result)
    if str(compat_result.get("result", "")).strip() != "complete":
        return dict(compat_result)
    access_result = evaluate_tool_access(tool_id="tool.logic_analyzer", authority_context=authority_context, has_physical_access=True)
    if str(access_result.get("result", "")).strip() != "complete":
        return dict(access_result)
    measurement_ids = [str(item).strip() for item in list(measurement_point_ids or []) if str(item).strip()]
    if not measurement_ids:
        return _refusal("refusal.tool.measurement_point_missing", "logic trace requires at least one measurement_point_id")
    capability_row = dict(tool_capability_rows_by_id().get("tool.logic_analyzer") or {})
    capability_ext = _as_map(capability_row.get("extensions"))
    max_duration_ticks = int(max(1, _as_int(capability_ext.get("max_trace_duration_ticks", 32), 32)))
    bounded_duration_ticks = int(max(1, min(max_duration_ticks, _as_int(duration_ticks, 1))))
    trace_request = {
        "request_id": "request.logic_trace.{}".format(
            canonical_sha256(
                {
                    "subject_id": str(subject_id or "").strip(),
                    "measurement_point_ids": list(measurement_ids),
                    "targets": [dict(item) for item in list(targets or []) if isinstance(item, Mapping)],
                    "current_tick": int(max(0, _as_int(current_tick, 0))),
                    "bounded_duration_ticks": bounded_duration_ticks,
                }
            )[:16]
        ),
        "subject_id": str(subject_id or "").strip(),
        "measurement_point_ids": list(measurement_ids),
        "tick_start": int(max(0, _as_int(current_tick, 0))),
        "tick_end": int(max(0, _as_int(current_tick, 0))) + bounded_duration_ticks,
        "sampling_policy_id": str(sampling_policy_id or "").strip() or "debug.sample.default",
        "extensions": {
            "targets": [dict(item) for item in list(targets or []) if isinstance(item, Mapping)],
            "source": "EMB1-5",
            "bounded_duration_ticks": bounded_duration_ticks,
        },
    }
    payload = {
        "result": "complete",
        "tool_id": "tool.logic_analyzer",
        "bounded_duration_ticks": bounded_duration_ticks,
        "trace_request": dict(trace_request),
        "process_sequence": [{"process_id": "process.logic_trace_start", "inputs": {"trace_request": dict(trace_request)}}],
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "build_logic_probe_task",
    "build_logic_trace_task",
]
