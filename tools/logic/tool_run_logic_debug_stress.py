#!/usr/bin/env python3
"""Run a deterministic LOGIC-7 debug stress scenario and summarize bounded trace behavior."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Iterable

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.logic.tool_replay_logic_window import _write_json
from tools.logic.tool_replay_trace_window import replay_trace_window_from_payload
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.testx.tests._logic_eval_test_utils import (
    compile_logic_network_fixture,
    load_eval_inputs,
    make_chain_network,
    seed_signal_requests,
)


def build_logic_debug_stress_scenario(
    *,
    repo_root: str,
    session_count: int = 12,
    tick_count: int = 6,
) -> dict:
    count = int(max(1, int(session_count)))
    total_ticks = int(max(2, int(tick_count)))
    network_id = "net.logic.debug.stress"
    _binding, logic_network_state = make_chain_network(
        network_id=network_id,
        binding_extensions={"logic_policy_id": "logic.default"},
    )
    fixture = compile_logic_network_fixture(
        repo_root=repo_root,
        network_id=network_id,
        logic_network_state=logic_network_state,
    )
    compile_eval = dict(fixture.get("compile_eval") or {})
    inputs = load_eval_inputs(repo_root)
    compiled_model_row = dict(compile_eval.get("compiled_model_row") or {})
    compiled_logic_network_state = copy.deepcopy(dict(compile_eval.get("logic_network_state") or logic_network_state))
    binding_rows = [dict(row) for row in list(compiled_logic_network_state.get("logic_network_binding_rows") or [])]
    if compiled_model_row and binding_rows:
        binding_rows[0]["extensions"] = dict(
            binding_rows[0].get("extensions") or {},
            compiled_model_id=str(compiled_model_row.get("compiled_model_id", "")).strip(),
            compiled_source_hash=str(compiled_model_row.get("source_hash", "")).strip(),
        )
        compiled_logic_network_state["logic_network_binding_rows"] = binding_rows

    signal_store_state = seed_signal_requests(
        signal_store_state=None,
        signal_requests=[
            {
                "tick": 0,
                "network_id": network_id,
                "element_id": "inst.logic.and.1",
                "port_id": "out.q",
                "signal_type_id": "signal.boolean",
                "carrier_type_id": "carrier.electrical",
                "value_payload": {"value": 1},
            },
            {
                "tick": 0,
                "network_id": network_id,
                "element_id": "inst.logic.not.1",
                "port_id": "out.q",
                "signal_type_id": "signal.boolean",
                "carrier_type_id": "carrier.electrical",
                "value_payload": {"value": 0},
            },
        ],
        inputs=inputs,
    )

    trace_requests = []
    for index in range(1, count + 1):
        if index % 2 == 0:
            trace_request = {
                "request_id": "request.logic.debug.stress.compiled.{}".format(index),
                "subject_id": network_id,
                "measurement_point_ids": ["measure.logic.network.compiled_summary"],
                "tick_start": 1,
                "tick_end": total_ticks,
                "sampling_policy_id": "debug.sample.lab_high",
                "extensions": {
                    "targets": [
                        {
                            "subject_id": network_id,
                            "network_id": network_id,
                            "measurement_point_id": "measure.logic.network.compiled_summary",
                        }
                    ]
                },
            }
            available_instrument_type_ids = ["instrument.logic_analyzer"]
        else:
            trace_request = {
                "request_id": "request.logic.debug.stress.output.{}".format(index),
                "subject_id": network_id,
                "measurement_point_ids": ["measure.logic.element.output_port"],
                "tick_start": 1,
                "tick_end": total_ticks,
                "sampling_policy_id": "debug.sample.lab_high",
                "extensions": {
                    "targets": [
                        {
                            "subject_id": network_id,
                            "network_id": network_id,
                            "element_id": "inst.logic.and.1",
                            "port_id": "out.q",
                            "measurement_point_id": "measure.logic.element.output_port",
                        }
                    ]
                },
            }
            available_instrument_type_ids = ["instrument.logic_probe"]
        trace_requests.append(
            {
                "tick": 1,
                "trace_request": trace_request,
                "authority_context": {
                    "privilege_level": "admin",
                    "entitlements": ["entitlement.inspect", "entitlement.admin"],
                },
                "has_physical_access": True,
                "available_instrument_type_ids": available_instrument_type_ids,
                "compute_profile_id": "compute.default",
            }
        )

    return {
        "scenario_id": "logic.debug.stress",
        "network_id": network_id,
        "logic_network_state": compiled_logic_network_state,
        "signal_store_state": signal_store_state,
        "logic_eval_state": {},
        "compiled_model_rows": [compiled_model_row] if compiled_model_row else [],
        "state_vector_snapshot_rows": [],
        "probe_requests": [],
        "trace_requests": trace_requests,
        "deterministic_fingerprint": canonical_sha256(
            {
                "network_id": network_id,
                "session_count": count,
                "tick_count": total_ticks,
                "compiled_model_id": str(compiled_model_row.get("compiled_model_id", "")).strip(),
            }
        ),
    }


def run_logic_debug_stress(
    *,
    repo_root: str,
    session_count: int = 12,
    tick_count: int = 6,
) -> dict:
    scenario = build_logic_debug_stress_scenario(
        repo_root=repo_root,
        session_count=session_count,
        tick_count=tick_count,
    )
    report = replay_trace_window_from_payload(repo_root=repo_root, payload=scenario)
    if str(report.get("result", "")).strip() != "complete":
        return report
    return {
        "result": "complete",
        "scenario_id": scenario["scenario_id"],
        "network_id": scenario["network_id"],
        "session_count": int(max(1, int(session_count))),
        "tick_count": int(max(2, int(tick_count))),
        "trace_session_count": int(len(list(report.get("trace_session_reports") or []))),
        "tick_report_count": int(len(list(report.get("tick_reports") or []))),
        "probe_artifact_count": int(report.get("probe_artifact_count", 0) or 0),
        "trace_artifact_count": int(report.get("trace_artifact_count", 0) or 0),
        "protocol_summary_count": int(report.get("protocol_summary_count", 0) or 0),
        "compiled_introspection_count": int(report.get("compiled_introspection_count", 0) or 0),
        "throttled_tick_count": int(
            sum(1 for row in list(report.get("tick_reports") or []) if str(dict(row).get("result", "")).strip() == "throttled")
        ),
        "logic_debug_request_hash_chain": str(report.get("logic_debug_request_hash_chain", "")),
        "logic_debug_trace_hash_chain": str(report.get("logic_debug_trace_hash_chain", "")),
        "logic_protocol_summary_hash_chain": str(report.get("logic_protocol_summary_hash_chain", "")),
        "forced_expand_event_hash_chain": str(report.get("forced_expand_event_hash_chain", "")),
        "deterministic_fingerprint": canonical_sha256(
            {
                "scenario_id": scenario["scenario_id"],
                "trace_session_count": int(len(list(report.get("trace_session_reports") or []))),
                "tick_report_count": int(len(list(report.get("tick_reports") or []))),
                "trace_artifact_count": int(report.get("trace_artifact_count", 0) or 0),
                "compiled_introspection_count": int(report.get("compiled_introspection_count", 0) or 0),
                "logic_debug_request_hash_chain": str(report.get("logic_debug_request_hash_chain", "")),
                "logic_debug_trace_hash_chain": str(report.get("logic_debug_trace_hash_chain", "")),
                "logic_protocol_summary_hash_chain": str(report.get("logic_protocol_summary_hash_chain", "")),
                "forced_expand_event_hash_chain": str(report.get("forced_expand_event_hash_chain", "")),
            }
        ),
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--session-count", type=int, default=12)
    parser.add_argument("--tick-count", type=int, default=6)
    parser.add_argument("--out-json", default="")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = run_logic_debug_stress(
        repo_root=args.repo_root,
        session_count=int(args.session_count),
        tick_count=int(args.tick_count),
    )
    if args.out_json:
        _write_json(os.path.join(args.repo_root, args.out_json.replace("/", os.sep)), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
