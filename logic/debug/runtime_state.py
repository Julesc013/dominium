"""Normalized runtime/evidence rows for LOGIC-7 debugging and instrumentation."""

from __future__ import annotations

from typing import Dict, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


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


def _normalize_trace_samples(samples: object) -> list[dict]:
    normalized = []
    for sample in sorted(
        (dict(item) for item in _as_list(samples) if isinstance(item, Mapping)),
        key=lambda item: (_as_int(item.get("tick"), 0), canonical_sha256(_canon(item))),
    ):
        values = [
            _canon(dict(row))
            for row in sorted(
                (dict(item) for item in _as_list(sample.get("values")) if isinstance(item, Mapping)),
                key=lambda item: (
                    _token(item.get("measurement_point_id")),
                    _token(item.get("target_key")),
                    _token(item.get("measurement_artifact_id")),
                    _token(item.get("observation_artifact_id")),
                ),
            )
        ]
        normalized.append({"tick": int(max(0, _as_int(sample.get("tick"), 0))), "values": values})
    return normalized


def build_logic_debug_probe_request_row(
    *,
    request_id: str,
    subject_id: str,
    measurement_point_id: str,
    tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "request_id": _token(request_id),
        "subject_id": _token(subject_id),
        "measurement_point_id": _token(measurement_point_id),
        "tick": int(max(0, _as_int(tick, 0))),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _canon(_as_map(extensions)),
    }
    if (not payload["request_id"]) or (not payload["subject_id"]) or (not payload["measurement_point_id"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_logic_debug_probe_request_rows(rows: object) -> list[dict]:
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in _as_list(rows) if isinstance(item, Mapping)),
        key=lambda item: (_as_int(item.get("tick"), 0), _token(item.get("request_id"))),
    ):
        normalized = build_logic_debug_probe_request_row(
            request_id=_token(row.get("request_id")),
            subject_id=_token(row.get("subject_id")),
            measurement_point_id=_token(row.get("measurement_point_id")),
            tick=_as_int(row.get("tick"), 0),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        request_id = _token(normalized.get("request_id"))
        if request_id:
            out[request_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_logic_debug_trace_request_row(
    *,
    request_id: str,
    subject_id: str,
    measurement_point_ids: object,
    tick_start: int,
    tick_end: int,
    sampling_policy_id: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "request_id": _token(request_id),
        "subject_id": _token(subject_id),
        "measurement_point_ids": sorted(_token(item) for item in _as_list(measurement_point_ids) if _token(item)),
        "tick_start": int(max(0, _as_int(tick_start, 0))),
        "tick_end": int(max(0, _as_int(tick_end, 0))),
        "sampling_policy_id": _token(sampling_policy_id),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _canon(_as_map(extensions)),
    }
    if payload["tick_end"] < payload["tick_start"]:
        payload["tick_end"] = int(payload["tick_start"])
    if (
        (not payload["request_id"])
        or (not payload["subject_id"])
        or (not payload["measurement_point_ids"])
        or (not payload["sampling_policy_id"])
    ):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_logic_debug_trace_request_rows(rows: object) -> list[dict]:
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in _as_list(rows) if isinstance(item, Mapping)),
        key=lambda item: (_as_int(item.get("tick_start"), 0), _token(item.get("request_id"))),
    ):
        normalized = build_logic_debug_trace_request_row(
            request_id=_token(row.get("request_id")),
            subject_id=_token(row.get("subject_id")),
            measurement_point_ids=_as_list(row.get("measurement_point_ids")),
            tick_start=_as_int(row.get("tick_start"), 0),
            tick_end=_as_int(row.get("tick_end"), 0),
            sampling_policy_id=_token(row.get("sampling_policy_id")),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        request_id = _token(normalized.get("request_id"))
        if request_id:
            out[request_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_logic_debug_trace_artifact_row(
    *,
    trace_id: str,
    request_id: str,
    samples: object,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "trace_id": _token(trace_id),
        "request_id": _token(request_id),
        "samples": _normalize_trace_samples(samples),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _canon(_as_map(extensions)),
    }
    if (not payload["trace_id"]) or (not payload["request_id"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_logic_debug_trace_artifact_rows(rows: object) -> list[dict]:
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in _as_list(rows) if isinstance(item, Mapping)),
        key=lambda item: (_token(item.get("request_id")), _token(item.get("trace_id"))),
    ):
        normalized = build_logic_debug_trace_artifact_row(
            trace_id=_token(row.get("trace_id")),
            request_id=_token(row.get("request_id")),
            samples=_as_list(row.get("samples")),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        trace_id = _token(normalized.get("trace_id"))
        if trace_id:
            out[trace_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_logic_debug_trace_session_row(
    *,
    session_id: str,
    request_id: str,
    subject_id: str,
    measurement_point_ids: object,
    tick_start: int,
    tick_end: int,
    sampling_policy_id: str,
    status: str,
    max_samples: int,
    sample_rows: object = None,
    sample_count: int = 0,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "session_id": _token(session_id),
        "request_id": _token(request_id),
        "subject_id": _token(subject_id),
        "measurement_point_ids": sorted(_token(item) for item in _as_list(measurement_point_ids) if _token(item)),
        "tick_start": int(max(0, _as_int(tick_start, 0))),
        "tick_end": int(max(0, _as_int(tick_end, 0))),
        "sampling_policy_id": _token(sampling_policy_id),
        "status": _token(status) or "active",
        "max_samples": int(max(1, _as_int(max_samples, 1))),
        "sample_rows": _normalize_trace_samples(sample_rows),
        "sample_count": int(max(0, _as_int(sample_count, 0))),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _canon(_as_map(extensions)),
    }
    if payload["tick_end"] < payload["tick_start"]:
        payload["tick_end"] = int(payload["tick_start"])
    if (
        (not payload["session_id"])
        or (not payload["request_id"])
        or (not payload["subject_id"])
        or (not payload["measurement_point_ids"])
        or (not payload["sampling_policy_id"])
    ):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_logic_debug_trace_session_rows(rows: object) -> list[dict]:
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in _as_list(rows) if isinstance(item, Mapping)),
        key=lambda item: (_token(item.get("session_id")), _token(item.get("request_id"))),
    ):
        normalized = build_logic_debug_trace_session_row(
            session_id=_token(row.get("session_id")),
            request_id=_token(row.get("request_id")),
            subject_id=_token(row.get("subject_id")),
            measurement_point_ids=_as_list(row.get("measurement_point_ids")),
            tick_start=_as_int(row.get("tick_start"), 0),
            tick_end=_as_int(row.get("tick_end"), 0),
            sampling_policy_id=_token(row.get("sampling_policy_id")),
            status=_token(row.get("status")) or "active",
            max_samples=_as_int(row.get("max_samples"), 1),
            sample_rows=_as_list(row.get("sample_rows")),
            sample_count=_as_int(row.get("sample_count"), 0),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        session_id = _token(normalized.get("session_id"))
        if session_id:
            out[session_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def _normalize_artifact_rows(rows: object) -> list[dict]:
    return [
        _canon(dict(row))
        for row in sorted(
            (dict(item) for item in _as_list(rows) if isinstance(item, Mapping)),
            key=lambda item: (_token(item.get("artifact_id") or item.get("trace_id")), canonical_sha256(_canon(item))),
        )
    ]


def normalize_logic_debug_state(state: Mapping[str, object] | None) -> dict:
    src = _as_map(state)
    return {
        "schema_version": "1.0.0",
        "logic_debug_probe_request_rows": normalize_logic_debug_probe_request_rows(src.get("logic_debug_probe_request_rows")),
        "logic_debug_trace_request_rows": normalize_logic_debug_trace_request_rows(src.get("logic_debug_trace_request_rows")),
        "logic_debug_trace_session_rows": normalize_logic_debug_trace_session_rows(src.get("logic_debug_trace_session_rows")),
        "logic_debug_probe_artifact_rows": _normalize_artifact_rows(src.get("logic_debug_probe_artifact_rows")),
        "logic_debug_trace_artifact_rows": normalize_logic_debug_trace_artifact_rows(src.get("logic_debug_trace_artifact_rows")),
        "logic_protocol_summary_artifact_rows": _normalize_artifact_rows(src.get("logic_protocol_summary_artifact_rows")),
        "logic_debug_explain_artifact_rows": _normalize_artifact_rows(src.get("logic_debug_explain_artifact_rows")),
        "compute_runtime_state": _canon(_as_map(src.get("compute_runtime_state"))),
        "extensions": _canon(_as_map(src.get("extensions"))),
    }


__all__ = [
    "build_logic_debug_probe_request_row",
    "build_logic_debug_trace_artifact_row",
    "build_logic_debug_trace_request_row",
    "build_logic_debug_trace_session_row",
    "normalize_logic_debug_probe_request_rows",
    "normalize_logic_debug_state",
    "normalize_logic_debug_trace_artifact_rows",
    "normalize_logic_debug_trace_request_rows",
    "normalize_logic_debug_trace_session_rows",
]
