#!/usr/bin/env python3
"""Replay a deterministic LOGIC-7 debug window and summarize trace proof hashes."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Iterable, Mapping

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from logic.debug import (
    normalize_logic_debug_state,
    process_logic_probe,
    process_logic_trace_end,
    process_logic_trace_start,
    process_logic_trace_tick,
)
from tools.logic.tool_replay_logic_window import _load_eval_inputs, _load_json, _write_json
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


def _load_debug_inputs(repo_root: str) -> dict:
    def read(rel_path: str) -> dict:
        return _load_json(os.path.join(repo_root, rel_path.replace("/", os.sep)))

    inputs = _load_eval_inputs(repo_root)
    inputs.update(
        {
            "debug_sampling_policy_registry_payload": read("data/registries/debug_sampling_policy_registry.json"),
            "instrumentation_surface_registry_payload": read("data/registries/instrumentation_surface_registry.json"),
            "access_policy_registry_payload": read("data/registries/access_policy_registry.json"),
            "measurement_model_registry_payload": read("data/registries/measurement_model_registry.json"),
        }
    )
    return inputs


def _logic_debug_request_hash_chain(state: Mapping[str, object]) -> str:
    probe_request_rows = [
        dict(row)
        for row in list(state.get("logic_debug_probe_request_rows") or [])
        if isinstance(row, Mapping)
    ]
    trace_request_rows = [
        dict(row)
        for row in list(state.get("logic_debug_trace_request_rows") or [])
        if isinstance(row, Mapping)
    ]
    return canonical_sha256(
        [
            {
                "request_id": _token(row.get("request_id")),
                "subject_id": _token(row.get("subject_id")),
                "measurement_point_id": _token(row.get("measurement_point_id")),
                "tick": int(max(0, _as_int(row.get("tick"), 0))),
            }
            for row in sorted(
                probe_request_rows,
                key=lambda item: (int(max(0, _as_int(item.get("tick"), 0))), _token(item.get("request_id"))),
            )
        ]
        + [
            {
                "request_id": _token(row.get("request_id")),
                "subject_id": _token(row.get("subject_id")),
                "measurement_point_ids": [_token(item) for item in list(row.get("measurement_point_ids") or []) if _token(item)],
                "tick_start": int(max(0, _as_int(row.get("tick_start"), 0))),
                "tick_end": int(max(0, _as_int(row.get("tick_end"), 0))),
                "sampling_policy_id": _token(row.get("sampling_policy_id")),
            }
            for row in sorted(
                trace_request_rows,
                key=lambda item: (int(max(0, _as_int(item.get("tick_start"), 0))), _token(item.get("request_id"))),
            )
        ]
    )


def _logic_debug_trace_hash_chain(state: Mapping[str, object]) -> str:
    trace_artifact_rows = [
        dict(row)
        for row in list(state.get("logic_debug_trace_artifact_rows") or [])
        if isinstance(row, Mapping)
    ]
    return canonical_sha256(
        [
            {
                "trace_id": _token(row.get("trace_id")),
                "request_id": _token(row.get("request_id")),
                "sample_count": int(
                    sum(
                        len(list(_as_map(sample).get("values") or []))
                        for sample in list(row.get("samples") or [])
                        if isinstance(sample, Mapping)
                    )
                ),
                "samples_hash": canonical_sha256(
                    [
                        {
                            "tick": int(max(0, _as_int(_as_map(sample).get("tick"), 0))),
                            "values": [
                                {
                                    "measurement_point_id": _token(_as_map(value).get("measurement_point_id")),
                                    "target_key": _token(_as_map(value).get("target_key")),
                                    "value_hash": _token(_as_map(value).get("value_hash")),
                                }
                                for value in list(_as_map(sample).get("values") or [])
                                if isinstance(value, Mapping)
                            ],
                        }
                        for sample in list(row.get("samples") or [])
                        if isinstance(sample, Mapping)
                    ]
                ),
            }
            for row in sorted(
                trace_artifact_rows,
                key=lambda item: (_token(item.get("request_id")), _token(item.get("trace_id"))),
            )
        ]
    )


def _logic_protocol_summary_hash_chain(state: Mapping[str, object]) -> str:
    protocol_rows = [
        dict(row)
        for row in list(state.get("logic_protocol_summary_artifact_rows") or [])
        if isinstance(row, Mapping)
    ]
    return canonical_sha256(
        [
            {
                "artifact_id": _token(row.get("artifact_id")),
                "signal_id": _token(row.get("signal_id")),
                "protocol_id": _token(row.get("protocol_id")),
                "tick": int(max(0, _as_int(row.get("tick"), 0))),
            }
            for row in sorted(
                protocol_rows,
                key=lambda item: (int(max(0, _as_int(item.get("tick"), 0))), _token(item.get("artifact_id"))),
            )
        ]
    )


def _forced_expand_event_hash_chain(rows: object) -> str:
    return canonical_sha256(
        [
            {
                "event_id": _token(row.get("event_id")),
                "capsule_id": _token(row.get("capsule_id")),
                "tick": int(max(0, _as_int(row.get("tick"), 0))),
                "reason_code": _token(row.get("reason_code")),
                "requested_fidelity": _token(row.get("requested_fidelity")),
            }
            for row in sorted(
                (dict(item) for item in list(rows or []) if isinstance(item, Mapping)),
                key=lambda item: (
                    int(max(0, _as_int(item.get("tick"), 0))),
                    _token(item.get("capsule_id")),
                    _token(item.get("event_id")),
                ),
            )
        ]
    )


def replay_trace_window_from_payload(*, repo_root: str, payload: Mapping[str, object]) -> dict:
    inputs = _load_debug_inputs(repo_root)
    logic_debug_state = normalize_logic_debug_state(payload.get("logic_debug_state"))
    signal_store_state = _as_map(payload.get("signal_store_state"))
    logic_network_state = _as_map(payload.get("logic_network_state"))
    logic_eval_state = _as_map(payload.get("logic_eval_state"))
    state_vector_snapshot_rows = [dict(row) for row in list(payload.get("state_vector_snapshot_rows") or []) if isinstance(row, Mapping)]
    compiled_model_rows = [dict(row) for row in list(payload.get("compiled_model_rows") or []) if isinstance(row, Mapping)]

    probe_operations = [
        dict(row)
        for row in sorted(
            (dict(item) for item in list(payload.get("probe_requests") or []) if isinstance(item, Mapping)),
            key=lambda item: (int(max(0, _as_int(item.get("tick"), 0))), _token(_as_map(item.get("probe_request")).get("request_id"))),
        )
    ]
    trace_operations = [
        dict(row)
        for row in sorted(
            (dict(item) for item in list(payload.get("trace_requests") or []) if isinstance(item, Mapping)),
            key=lambda item: (
                int(max(0, _as_int(_as_map(item.get("trace_request")).get("tick_start"), 0))),
                _token(_as_map(item.get("trace_request")).get("request_id")),
            ),
        )
    ]

    probe_reports = []
    tick_reports = []
    trace_session_reports = []
    forced_expand_event_rows = []
    compiled_introspection_artifact_rows = []
    session_controls: dict[str, dict] = {}

    for operation in probe_operations:
        probe_request = _as_map(operation.get("probe_request"))
        result = process_logic_probe(
            current_tick=int(max(0, _as_int(operation.get("tick"), _as_int(probe_request.get("tick"), 0)))),
            logic_debug_state=logic_debug_state,
            signal_store_state=signal_store_state,
            logic_network_state=logic_network_state,
            logic_eval_state=logic_eval_state,
            probe_request=probe_request,
            state_vector_snapshot_rows=state_vector_snapshot_rows,
            compiled_model_rows=compiled_model_rows,
            protocol_registry_payload=inputs["protocol_registry_payload"],
            instrumentation_surface_registry_payload=inputs["instrumentation_surface_registry_payload"],
            access_policy_registry_payload=inputs["access_policy_registry_payload"],
            measurement_model_registry_payload=inputs["measurement_model_registry_payload"],
            compute_budget_profile_registry_payload=inputs["compute_budget_profile_registry_payload"],
            compute_degrade_policy_registry_payload=inputs["compute_degrade_policy_registry_payload"],
            compute_budget_profile_id=_token(operation.get("compute_profile_id")) or "compute.default",
            authority_context=_as_map(operation.get("authority_context")),
            has_physical_access=bool(operation.get("has_physical_access", False)),
            available_instrument_type_ids=_as_list(operation.get("available_instrument_type_ids")),
        )
        logic_debug_state = normalize_logic_debug_state(result.get("logic_debug_state"))
        forced_expand_event_rows.extend(
            dict(row) for row in list(result.get("forced_expand_event_rows") or []) if isinstance(row, Mapping)
        )
        compiled_introspection_artifact_rows.extend(
            dict(row) for row in list(result.get("compiled_introspection_artifact_rows") or []) if isinstance(row, Mapping)
        )
        probe_reports.append(
            {
                "tick": int(max(0, _as_int(operation.get("tick"), _as_int(probe_request.get("tick"), 0)))),
                "request_id": _token(_as_map(result.get("probe_request_row")).get("request_id")) or _token(probe_request.get("request_id")),
                "measurement_point_id": _token(probe_request.get("measurement_point_id")),
                "result": _token(result.get("result")),
                "reason_code": _token(result.get("reason_code")),
            }
        )
        if _token(result.get("result")) not in {"complete", "throttled"}:
            return {
                "result": "refused",
                "reason_code": _token(result.get("reason_code")) or "refusal.logic.debug_probe",
                "probe_reports": probe_reports,
            }

    for operation in trace_operations:
        trace_request = _as_map(operation.get("trace_request"))
        result = process_logic_trace_start(
            current_tick=int(max(0, _as_int(operation.get("tick"), _as_int(trace_request.get("tick_start"), 0)))),
            logic_debug_state=logic_debug_state,
            logic_network_state=logic_network_state,
            trace_request=trace_request,
            compiled_model_rows=compiled_model_rows,
            debug_sampling_policy_registry_payload=inputs["debug_sampling_policy_registry_payload"],
            compute_budget_profile_registry_payload=inputs["compute_budget_profile_registry_payload"],
            compute_degrade_policy_registry_payload=inputs["compute_degrade_policy_registry_payload"],
            compute_budget_profile_id=_token(operation.get("compute_profile_id")) or "compute.default",
            has_physical_access=bool(operation.get("has_physical_access", False)),
        )
        logic_debug_state = normalize_logic_debug_state(result.get("logic_debug_state"))
        forced_expand_event_rows.extend(
            dict(row) for row in list(result.get("forced_expand_event_rows") or []) if isinstance(row, Mapping)
        )
        session_row = _as_map(result.get("trace_session_row"))
        session_id = _token(session_row.get("session_id"))
        if session_id:
            session_controls[session_id] = {
                "authority_context": _as_map(operation.get("authority_context")),
                "has_physical_access": bool(operation.get("has_physical_access", False)),
                "available_instrument_type_ids": _as_list(operation.get("available_instrument_type_ids")),
                "compute_profile_id": _token(operation.get("compute_profile_id")) or "compute.default",
            }
        if _token(result.get("result")) not in {"complete", "throttled"}:
            return {
                "result": "refused",
                "reason_code": _token(result.get("reason_code")) or "refusal.logic.trace_start",
                "probe_reports": probe_reports,
            }

    for session_id in sorted(session_controls.keys()):
        session_row = next(
            (dict(row) for row in list(logic_debug_state.get("logic_debug_trace_session_rows") or []) if _token(_as_map(row).get("session_id")) == session_id),
            {},
        )
        tick_start = int(max(0, _as_int(session_row.get("tick_start"), 0)))
        tick_end = int(max(tick_start, _as_int(session_row.get("tick_end"), tick_start)))
        control = _as_map(session_controls.get(session_id))
        for tick in range(tick_start, tick_end + 1):
            result = process_logic_trace_tick(
                current_tick=tick,
                logic_debug_state=logic_debug_state,
                signal_store_state=signal_store_state,
                logic_network_state=logic_network_state,
                logic_eval_state=logic_eval_state,
                trace_tick_request={"session_id": session_id, "compute_profile_id": _token(control.get("compute_profile_id")) or "compute.default"},
                state_vector_snapshot_rows=state_vector_snapshot_rows,
                compiled_model_rows=compiled_model_rows,
                protocol_registry_payload=inputs["protocol_registry_payload"],
                instrumentation_surface_registry_payload=inputs["instrumentation_surface_registry_payload"],
                access_policy_registry_payload=inputs["access_policy_registry_payload"],
                measurement_model_registry_payload=inputs["measurement_model_registry_payload"],
                compute_budget_profile_registry_payload=inputs["compute_budget_profile_registry_payload"],
                compute_degrade_policy_registry_payload=inputs["compute_degrade_policy_registry_payload"],
                compute_budget_profile_id=_token(control.get("compute_profile_id")) or "compute.default",
                authority_context=_as_map(control.get("authority_context")),
                has_physical_access=bool(control.get("has_physical_access", False)),
                available_instrument_type_ids=_as_list(control.get("available_instrument_type_ids")),
            )
            logic_debug_state = normalize_logic_debug_state(result.get("logic_debug_state"))
            forced_expand_event_rows.extend(
                dict(row) for row in list(result.get("forced_expand_event_rows") or []) if isinstance(row, Mapping)
            )
            compiled_introspection_artifact_rows.extend(
                dict(row) for row in list(result.get("compiled_introspection_artifact_rows") or []) if isinstance(row, Mapping)
            )
            tick_reports.append(
                {
                    "tick": tick,
                    "session_id": session_id,
                    "result": _token(result.get("result")),
                    "reason_code": _token(result.get("reason_code")),
                    "trace_artifact_count": int(len(list(result.get("trace_artifact_rows") or []))),
                }
            )
            if _token(result.get("result")) not in {"complete", "throttled"}:
                return {
                    "result": "refused",
                    "reason_code": _token(result.get("reason_code")) or "refusal.logic.trace_tick",
                    "probe_reports": probe_reports,
                    "tick_reports": tick_reports,
                }

    for session_id in sorted(session_controls.keys()):
        result = process_logic_trace_end(
            current_tick=max((int(report["tick"]) for report in tick_reports if _token(report.get("session_id")) == session_id), default=0),
            logic_debug_state=logic_debug_state,
            trace_end_request={"session_id": session_id},
        )
        logic_debug_state = normalize_logic_debug_state(result.get("logic_debug_state"))
        trace_session_reports.append(
            {
                "session_id": session_id,
                "trace_id": _token(_as_map(result.get("trace_artifact_row")).get("trace_id")),
                "result": _token(result.get("result")),
                "reason_code": _token(result.get("reason_code")),
            }
        )
        if _token(result.get("result")) != "complete":
            return {
                "result": "refused",
                "reason_code": _token(result.get("reason_code")) or "refusal.logic.trace_end",
                "probe_reports": probe_reports,
                "tick_reports": tick_reports,
                "trace_session_reports": trace_session_reports,
            }

    report = {
        "result": "complete",
        "probe_reports": probe_reports,
        "tick_reports": tick_reports,
        "trace_session_reports": trace_session_reports,
        "logic_debug_request_hash_chain": _logic_debug_request_hash_chain(logic_debug_state),
        "logic_debug_trace_hash_chain": _logic_debug_trace_hash_chain(logic_debug_state),
        "logic_protocol_summary_hash_chain": _logic_protocol_summary_hash_chain(logic_debug_state),
        "forced_expand_event_hash_chain": _forced_expand_event_hash_chain(forced_expand_event_rows),
        "probe_artifact_count": int(len(list(logic_debug_state.get("logic_debug_probe_artifact_rows") or []))),
        "trace_artifact_count": int(len(list(logic_debug_state.get("logic_debug_trace_artifact_rows") or []))),
        "protocol_summary_count": int(len(list(logic_debug_state.get("logic_protocol_summary_artifact_rows") or []))),
        "compiled_introspection_count": int(len(compiled_introspection_artifact_rows)),
        "final_logic_debug_state": logic_debug_state,
        "forced_expand_event_rows": forced_expand_event_rows,
        "compiled_introspection_artifact_rows": compiled_introspection_artifact_rows,
    }
    report["proof_surface"] = {
        "logic_debug_request_hash_chain": report["logic_debug_request_hash_chain"],
        "logic_debug_trace_hash_chain": report["logic_debug_trace_hash_chain"],
        "logic_protocol_summary_hash_chain": report["logic_protocol_summary_hash_chain"],
        "forced_expand_event_hash_chain": report["forced_expand_event_hash_chain"],
    }
    report["deterministic_fingerprint"] = canonical_sha256(
        {
            "probe_reports": report["probe_reports"],
            "tick_reports": report["tick_reports"],
            "trace_session_reports": report["trace_session_reports"],
            "proof_surface": report["proof_surface"],
            "probe_artifact_count": report["probe_artifact_count"],
            "trace_artifact_count": report["trace_artifact_count"],
            "protocol_summary_count": report["protocol_summary_count"],
            "compiled_introspection_count": report["compiled_introspection_count"],
        }
    )
    return report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--scenario-json", required=True)
    parser.add_argument("--out-json", default="")
    args = parser.parse_args(list(argv) if argv is not None else None)

    payload = _load_json(os.path.join(args.repo_root, args.scenario_json.replace("/", os.sep)))
    report = replay_trace_window_from_payload(repo_root=args.repo_root, payload=payload)
    if args.out_json:
        _write_json(os.path.join(args.repo_root, args.out_json.replace("/", os.sep)), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if _token(report.get("result")) == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
