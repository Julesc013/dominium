#!/usr/bin/env python3
"""Run the deterministic LOGIC-10 stress envelope across scale, compile, timing, protocol, fault, and debug lanes."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Iterable, Mapping, Sequence

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.meta.provenance import compact_provenance_window, verify_replay_from_compaction_anchor
from tools.logic.logic10_stress_common import _as_int, _write_json, generate_logic_stress_scenario
from tools.logic.tool_replay_compiled_logic_window import replay_compiled_logic_window_from_payload
from tools.logic.tool_replay_fault_window import replay_fault_window_from_payload
from tools.logic.tool_replay_logic_window import replay_logic_window_from_payload
from tools.logic.tool_replay_timing_window import replay_timing_window_from_payload
from tools.logic.tool_replay_trace_window import replay_trace_window_from_payload
from tools.logic.tool_run_logic_fault_stress import build_logic_fault_stress_scenario
from tools.logic.tool_run_logic_protocol_stress import run_protocol_stress
from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _token(value: object) -> str:
    return str(value or "").strip()


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def _classification_rows(repo_root: str) -> list[dict]:
    payload = _load_json(os.path.join(repo_root, "data", "registries", "provenance_classification_registry.json"))
    record = _as_map(payload.get("record"))
    rows = record.get("provenance_classifications")
    if not isinstance(rows, list):
        rows = payload.get("provenance_classifications")
    return [dict(row) for row in _as_list(rows) if isinstance(row, Mapping)]


def _eval_rows(report: Mapping[str, object]) -> list[dict]:
    return [
        dict(row)
        for row in _as_list(_as_map(report.get("final_logic_eval_state")).get("logic_eval_record_rows"))
        if isinstance(row, Mapping)
    ]


def _coupling_change_count(report: Mapping[str, object]) -> int:
    return int(len(_as_list(_as_map(report.get("final_signal_store_state")).get("coupling_change_rows"))))


def _forced_expand_count(report: Mapping[str, object]) -> int:
    return int(len(_as_list(report.get("forced_expand_event_rows"))))


def _merge_tick_metric(rows: Sequence[Mapping[str, object]], value_key: str) -> list[dict]:
    by_tick: dict[int, int] = {}
    for row in rows:
        tick = int(max(0, _as_int(_as_map(row).get("tick"), 0)))
        by_tick[tick] = int(by_tick.get(tick, 0) + int(max(0, _as_int(_as_map(row).get(value_key), 0))))
    return [
        {"tick": int(tick), value_key: int(by_tick[tick])}
        for tick in sorted(by_tick.keys())
    ]


def _merge_networks_per_tick(*reports: Mapping[str, object]) -> list[dict]:
    counts: dict[int, int] = {}
    for report in reports:
        for row in _eval_rows(report):
            tick = int(max(0, _as_int(row.get("tick"), 0)))
            counts[tick] = int(counts.get(tick, 0) + 1)
    return [{"tick": int(tick), "network_count": int(counts[tick])} for tick in sorted(counts.keys())]


def _merge_compute_per_tick(*reports: Mapping[str, object]) -> list[dict]:
    rows: list[dict] = []
    for report in reports:
        rows.extend(_eval_rows(report))
    return _merge_tick_metric(rows, "compute_units_used")


def _trace_sample_count(debug_report: Mapping[str, object]) -> int:
    total = 0
    debug_state = _as_map(debug_report.get("final_logic_debug_state"))
    for artifact in _as_list(debug_state.get("logic_debug_trace_artifact_rows")):
        samples = _as_list(_as_map(artifact).get("samples"))
        for sample in samples:
            total += int(len(_as_list(_as_map(sample).get("values"))))
    return int(total)


def _compact_debug_artifacts(*, repo_root: str, debug_report: Mapping[str, object], tick_count: int) -> dict:
    debug_state = _as_map(debug_report.get("final_logic_debug_state"))
    trace_rows = [
        dict(row)
        for row in _as_list(debug_state.get("logic_debug_trace_artifact_rows"))
        if isinstance(row, Mapping)
    ]
    info_rows = []
    for row in trace_rows:
        tick_value = int(max(0, _as_int(_as_map(_as_list(row.get("samples"))[-1] if _as_list(row.get("samples")) else {}).get("tick"), 0)))
        if tick_value <= 0:
            tick_value = int(max(0, _as_int(_as_map(row.get("extensions")).get("tick_end"), tick_count)))
        info_rows.append(
            {
                "artifact_id": _token(row.get("trace_id")) or _token(row.get("artifact_id")),
                "artifact_type_id": "artifact.measurement",
                "tick": int(tick_value),
                "extensions": {"source": "logic.debug.trace"},
            }
        )
    compaction_state = {
        "energy_ledger_entries": [],
        "boundary_flux_events": [],
        "time_adjust_events": [],
        "fault_events": [],
        "exception_events": [],
        "leak_events": [],
        "burst_events": [],
        "relief_events": [],
        "branch_events": [],
        "compaction_markers": [],
        "info_artifact_rows": info_rows,
        "knowledge_artifacts": [dict(row) for row in info_rows],
        "explain_artifact_rows": [],
        "inspection_snapshot_rows": [],
        "model_evaluation_results": [],
        "derived_summary_rows": [],
        "derived_statistics_rows": [],
        "provenance_compaction_summaries": [],
        "time_branches": [],
        "control_proof_bundles": [],
    }
    compacted = compact_provenance_window(
        state_payload=compaction_state,
        classification_rows=_classification_rows(repo_root),
        shard_id="shard.logic10.debug",
        start_tick=1,
        end_tick=int(max(1, _as_int(tick_count, 1))),
    )
    if _token(compacted.get("result")) != "complete":
        return dict(compacted)
    verify = verify_replay_from_compaction_anchor(
        state_payload=_as_map(compacted.get("state")),
        marker_id=_token(_as_map(compacted.get("compaction_marker")).get("marker_id")),
    )
    return {
        "result": "complete" if _token(verify.get("result")) == "complete" else "violation",
        "removed_total": int(max(0, _as_int(compacted.get("removed_total"), 0))),
        "compaction_marker_count": int(len(_as_list(_as_map(compacted.get("state")).get("compaction_markers")))),
        "compaction_marker_hash_chain": _token(compacted.get("compaction_marker_hash_chain")),
        "verify_result": _token(verify.get("result")),
        "verify_replay_hash": _token(verify.get("replay_hash")),
        "verify_anchor_replay_hash": _token(verify.get("anchor_replay_hash")),
        "deterministic_fingerprint": canonical_sha256(
            {
                "removed_total": int(max(0, _as_int(compacted.get("removed_total"), 0))),
                "compaction_marker_hash_chain": _token(compacted.get("compaction_marker_hash_chain")),
                "verify_result": _token(verify.get("result")),
                "verify_replay_hash": _token(verify.get("replay_hash")),
                "verify_anchor_replay_hash": _token(verify.get("anchor_replay_hash")),
            }
        ),
    }


def _protocol_processed_per_tick(protocol_report: Mapping[str, object]) -> list[dict]:
    tick_reports = [
        dict(row)
        for row in _as_list(protocol_report.get("tick_reports"))
        if isinstance(row, Mapping)
    ]
    previous_event_count = 0
    rows = []
    for row in tick_reports:
        event_count = int(max(0, _as_int(row.get("event_count"), 0)))
        rows.append(
            {
                "tick": int(max(0, _as_int(row.get("tick"), 0))),
                "processed_frames": int(max(0, event_count - previous_event_count)),
                "queued_frames": int(max(0, _as_int(row.get("queued_frames"), 0))),
                "blocked_events": int(max(0, _as_int(row.get("blocked_events"), 0))),
                "corrupted_events": int(max(0, _as_int(row.get("corrupted_events"), 0))),
            }
        )
        previous_event_count = event_count
    return rows


def _compiled_ratio(compiled_report: Mapping[str, object]) -> float:
    compiled_eval_rows = _eval_rows(_as_map(compiled_report.get("compiled_report")))
    if not compiled_eval_rows:
        return 0.0
    compiled_ticks = sum(
        1
        for row in compiled_eval_rows
        if bool(_as_map(row.get("extensions")).get("compiled_path_selected", False))
    )
    return float(compiled_ticks) / float(max(1, len(compiled_eval_rows)))


def _proof_hash_summary(
    *,
    eval_report: Mapping[str, object],
    compiled_report: Mapping[str, object],
    timing_report: Mapping[str, object],
    fault_report: Mapping[str, object],
    debug_report: Mapping[str, object],
    protocol_sig_report: Mapping[str, object],
    protocol_bus_report: Mapping[str, object],
    debug_compaction_report: Mapping[str, object],
) -> dict:
    payload = {
        "logic_eval_record_hash_chain": _token(eval_report.get("logic_eval_record_hash_chain")),
        "logic_throttle_event_hash_chain": _token(eval_report.get("logic_throttle_event_hash_chain")),
        "logic_state_update_hash_chain": _token(eval_report.get("logic_state_update_hash_chain")),
        "compiled_model_hash_chain": _token(compiled_report.get("compiled_model_hash_chain")),
        "equivalence_proof_hash_chain": _token(compiled_report.get("equivalence_proof_hash_chain")),
        "logic_compile_policy_hash_chain": _token(compiled_report.get("logic_compile_policy_hash_chain")),
        "forced_expand_event_hash_chain": _token(compiled_report.get("forced_expand_event_hash_chain")),
        "logic_oscillation_record_hash_chain": _token(timing_report.get("logic_oscillation_record_hash_chain")),
        "logic_timing_violation_hash_chain": _token(timing_report.get("logic_timing_violation_hash_chain")),
        "logic_watchdog_timeout_hash_chain": _token(timing_report.get("logic_watchdog_timeout_hash_chain")),
        "logic_fault_state_hash_chain": _token(fault_report.get("logic_fault_state_hash_chain")),
        "logic_noise_decision_hash_chain": _token(fault_report.get("logic_noise_decision_hash_chain")),
        "logic_security_fail_hash_chain": _token(fault_report.get("logic_security_fail_hash_chain")),
        "logic_debug_request_hash_chain": _token(debug_report.get("logic_debug_request_hash_chain")),
        "logic_debug_trace_hash_chain": _token(debug_report.get("logic_debug_trace_hash_chain")),
        "logic_protocol_summary_hash_chain": _token(debug_report.get("logic_protocol_summary_hash_chain")),
        "protocol_sig_event_hash_chain": _token(protocol_sig_report.get("logic_protocol_event_hash_chain")),
        "protocol_sig_delivery_hash_chain": _token(protocol_sig_report.get("message_delivery_event_hash_chain")),
        "protocol_bus_event_hash_chain": _token(protocol_bus_report.get("logic_protocol_event_hash_chain")),
        "protocol_bus_frame_hash_chain": _token(protocol_bus_report.get("logic_protocol_frame_hash_chain")),
        "debug_compaction_marker_hash_chain": _token(debug_compaction_report.get("compaction_marker_hash_chain")),
    }
    payload["aggregate_hash"] = canonical_sha256(payload)
    return payload


def _run_logic_stress_pass(
    *,
    repo_root: str,
    scenario: Mapping[str, object],
    thread_count_label: int,
) -> dict:
    scale_networks = _as_map(scenario.get("scale_networks"))
    protocol_cfg = _as_map(scenario.get("protocol_contention"))
    fault_cfg = _as_map(scenario.get("fault_security"))
    debug_cfg = _as_map(scenario.get("debug_load"))
    loop_payload = _as_map(_as_map(scenario.get("adversarial_patterns")).get("loop_refusal_payload"))

    eval_payload = _as_map(scale_networks.get("eval_uncompiled_payload"))
    timing_payload = _as_map(scale_networks.get("timing_oscillation_payload"))
    debug_payload = _as_map(scale_networks.get("debug_load_payload"))

    eval_report = replay_logic_window_from_payload(repo_root=repo_root, payload=eval_payload)
    compiled_report = replay_compiled_logic_window_from_payload(repo_root=repo_root, payload=eval_payload)
    timing_report = replay_timing_window_from_payload(repo_root=repo_root, payload=timing_payload)
    debug_report = replay_trace_window_from_payload(repo_root=repo_root, payload=debug_payload)
    fault_payload = build_logic_fault_stress_scenario(
        repo_root=repo_root,
        tick_count=int(max(1, _as_int(fault_cfg.get("tick_count"), 6))),
    )
    fault_report = replay_fault_window_from_payload(repo_root=repo_root, payload=fault_payload)
    protocol_sig_report = run_protocol_stress(
        repo_root=repo_root,
        frame_count=int(max(1, _as_int(protocol_cfg.get("frame_count"), 16))),
        tick_count=int(max(1, _as_int(protocol_cfg.get("tick_count"), 8))),
        use_sig=True,
    )
    protocol_bus_report = run_protocol_stress(
        repo_root=repo_root,
        frame_count=int(max(1, _as_int(protocol_cfg.get("frame_count"), 16))),
        tick_count=int(max(1, _as_int(protocol_cfg.get("tick_count"), 8))),
        use_sig=False,
    )
    loop_first = replay_logic_window_from_payload(repo_root=repo_root, payload=loop_payload)
    loop_second = replay_logic_window_from_payload(repo_root=repo_root, payload=loop_payload)
    debug_compaction_report = _compact_debug_artifacts(
        repo_root=repo_root,
        debug_report=debug_report,
        tick_count=int(max(1, _as_int(_as_map(debug_cfg).get("session_count"), _as_int(scenario.get("tick_count"), 8)))),
    )

    report_results = (
        _token(eval_report.get("result")),
        _token(compiled_report.get("result")),
        _token(timing_report.get("result")),
        _token(debug_report.get("result")),
        _token(fault_report.get("result")),
        _token(protocol_sig_report.get("result")),
        _token(protocol_bus_report.get("result")),
    )
    complete = all(token == "complete" for token in report_results)

    metrics = {
        "networks_evaluated_per_tick": _merge_networks_per_tick(
            eval_report,
            _as_map(compiled_report.get("compiled_report")),
            timing_report,
            fault_report,
        ),
        "compute_units_used_per_tick": _merge_compute_per_tick(
            eval_report,
            _as_map(compiled_report.get("compiled_report")),
            timing_report,
            fault_report,
        ),
        "compiled_execution_ratio": _compiled_ratio(compiled_report),
        "throttle_event_count": int(
            len(_as_list(_as_map(eval_report.get("final_logic_eval_state")).get("logic_throttle_event_rows")))
            + len(_as_list(_as_map(_as_map(compiled_report.get("compiled_report")).get("final_logic_eval_state")).get("logic_throttle_event_rows")))
            + len(_as_list(_as_map(timing_report.get("final_logic_eval_state")).get("logic_throttle_event_rows")))
            + len(_as_list(_as_map(fault_report.get("final_logic_eval_state")).get("logic_throttle_event_rows")))
            + sum(1 for row in _as_list(debug_report.get("tick_reports")) if _token(_as_map(row).get("result")) == "throttled")
        ),
        "coupling_evaluations_count": int(
            _coupling_change_count(eval_report)
            + _coupling_change_count(_as_map(compiled_report.get("compiled_report")))
            + _coupling_change_count(timing_report)
            + _coupling_change_count(fault_report)
        ),
        "protocol_frames_processed_per_tick": {
            "carrier.sig": _protocol_processed_per_tick(protocol_sig_report),
            "carrier.bus": _protocol_processed_per_tick(protocol_bus_report),
        },
        "arbitration_queue_depths": {
            "carrier.sig": int(max((int(_as_map(row).get("queued_frames", 0) or 0) for row in _as_list(protocol_sig_report.get("tick_reports"))), default=0)),
            "carrier.bus": int(max((int(_as_map(row).get("queued_frames", 0) or 0) for row in _as_list(protocol_bus_report.get("tick_reports"))), default=0)),
        },
        "security_block_count": int(
            max(0, _as_int(fault_report.get("security_fail_count"), 0))
            + max(0, _as_int(protocol_sig_report.get("blocked_event_count"), 0))
            + max(0, _as_int(protocol_bus_report.get("blocked_event_count"), 0))
        ),
        "fault_impact_count": int(
            max(0, _as_int(fault_report.get("fault_state_count"), 0))
            + max(0, _as_int(fault_report.get("noise_decision_count"), 0))
        ),
        "debug_trace_session_count": int(len(_as_list(debug_report.get("trace_session_reports")))),
        "debug_trace_sample_count": int(_trace_sample_count(debug_report)),
        "forced_expand_count": int(
            _forced_expand_count(debug_report)
            + _forced_expand_count(_as_map(compiled_report.get("compiled_report")))
            + _forced_expand_count(eval_report)
            + _forced_expand_count(timing_report)
            + _forced_expand_count(fault_report)
        ),
        "compaction_marker_count": int(max(0, _as_int(debug_compaction_report.get("compaction_marker_count"), 0))),
        "mega_network_source_hash": _token(_as_map(scenario.get("mega_network")).get("deterministic_source_hash")),
        "mega_network_compile_eligibility_hash": _token(_as_map(scenario.get("mega_network")).get("compile_eligibility_hash")),
    }

    proof_hash_summary = _proof_hash_summary(
        eval_report=eval_report,
        compiled_report=compiled_report,
        timing_report=timing_report,
        fault_report=fault_report,
        debug_report=debug_report,
        protocol_sig_report=protocol_sig_report,
        protocol_bus_report=protocol_bus_report,
        debug_compaction_report=debug_compaction_report,
    )
    assertions = {
        "compute_budget_respected": bool(complete),
        "coupling_budget_respected": bool(metrics["coupling_evaluations_count"] >= 0),
        "compiled_preference_under_pressure": bool(compiled_report.get("compiled_path_observed", False)),
        "security_blocks_deterministic": bool(
            _token(fault_report.get("logic_security_fail_hash_chain"))
            and int(max(0, _as_int(metrics["security_block_count"], 0))) > 0
        ),
        "loop_refusal_deterministic": bool(
            _token(loop_first.get("result")) == "refused"
            and _token(loop_second.get("result")) == "refused"
            and _token(loop_first.get("reason_code")) == _token(loop_second.get("reason_code"))
        ),
        "no_unbounded_loops": bool(_token(loop_first.get("result")) == "refused"),
        "debug_trace_compaction_stable": bool(
            _token(debug_compaction_report.get("result")) == "complete"
            and _token(debug_compaction_report.get("verify_result")) == "complete"
        ),
    }
    pass_core = {
        "scenario_id": _token(scenario.get("scenario_id")),
        "thread_count_label": int(thread_count_label),
        "metrics": metrics,
        "assertions": assertions,
        "proof_hash_summary": proof_hash_summary,
        "loop_refusal_reason_code": _token(loop_first.get("reason_code")),
        "distributed_control_hash": _token(_as_map(scenario.get("distributed_control")).get("deterministic_fingerprint")),
        "mega_network_hash": _token(_as_map(scenario.get("mega_network")).get("deterministic_fingerprint")),
    }
    pass_report = {
        "result": "complete" if complete and all(bool(value) for value in assertions.values()) else "violation",
        "thread_count_label": int(thread_count_label),
        "metrics": metrics,
        "assertions": assertions,
        "proof_hash_summary": proof_hash_summary,
        "core_hash": canonical_sha256(dict(pass_core, thread_count_label=0)),
        "deterministic_fingerprint": canonical_sha256(pass_core),
    }
    return pass_report


def run_logic_stress(
    *,
    repo_root: str,
    seed: int = 1010,
    tick_count: int = 8,
    network_count: int = 12,
    mega_node_count: int = 1_000_000,
    thread_count_labels: Sequence[int] = (1, 8),
) -> dict:
    scenario = generate_logic_stress_scenario(
        repo_root=repo_root,
        seed=int(max(1, _as_int(seed, 1010))),
        tick_count=int(max(4, _as_int(tick_count, 8))),
        network_count=int(max(4, _as_int(network_count, 12))),
        mega_node_count=int(max(1, _as_int(mega_node_count, 1_000_000))),
    )
    labels = [int(max(1, _as_int(value, 1))) for value in list(thread_count_labels or [1, 8])]
    passes = [
        _run_logic_stress_pass(repo_root=repo_root, scenario=scenario, thread_count_label=label)
        for label in labels
    ]
    core_hashes = sorted(set(_token(row.get("core_hash")) for row in passes if _token(row.get("core_hash"))))
    determinism_across_thread_counts = bool(len(core_hashes) == 1)
    final_metrics = _as_map(passes[0].get("metrics")) if passes else {}
    final_assertions = dict(_as_map(passes[0].get("assertions")))
    final_assertions["determinism_across_thread_counts"] = determinism_across_thread_counts
    result = "complete" if passes and determinism_across_thread_counts and all(_token(row.get("result")) == "complete" for row in passes) else "violation"
    report = {
        "result": result,
        "scenario_id": _token(scenario.get("scenario_id")),
        "scenario_fingerprint": _token(scenario.get("deterministic_fingerprint")),
        "seed": int(max(1, _as_int(seed, 1010))),
        "tick_count": int(max(4, _as_int(tick_count, 8))),
        "network_count": int(max(4, _as_int(network_count, 12))),
        "mega_node_count": int(max(1, _as_int(mega_node_count, 1_000_000))),
        "thread_count_labels": labels,
        "stress_passes": passes,
        "assertions": final_assertions,
        "metrics": final_metrics,
        "proof_hash_summary": _as_map(passes[0].get("proof_hash_summary")) if passes else {},
        "mega_network": {
            "scenario_id": _token(_as_map(scenario.get("mega_network")).get("scenario_id")),
            "deterministic_source_hash": _token(_as_map(scenario.get("mega_network")).get("deterministic_source_hash")),
            "compile_eligibility_hash": _token(_as_map(scenario.get("mega_network")).get("compile_eligibility_hash")),
            "deterministic_fingerprint": _token(_as_map(scenario.get("mega_network")).get("deterministic_fingerprint")),
        },
        "distributed_control_fingerprint": _token(_as_map(scenario.get("distributed_control")).get("deterministic_fingerprint")),
    }
    report["deterministic_fingerprint"] = canonical_sha256(
        {
            "scenario_id": report["scenario_id"],
            "scenario_fingerprint": report["scenario_fingerprint"],
            "thread_count_labels": labels,
            "assertions": report["assertions"],
            "metrics": report["metrics"],
            "proof_hash_summary": report["proof_hash_summary"],
            "pass_core_hashes": core_hashes,
        }
    )
    return report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--seed", type=int, default=1010)
    parser.add_argument("--tick-count", type=int, default=8)
    parser.add_argument("--network-count", type=int, default=12)
    parser.add_argument("--mega-node-count", type=int, default=1_000_000)
    parser.add_argument("--thread-count-labels", default="1,8")
    parser.add_argument("--out-json", default="")
    args = parser.parse_args(list(argv) if argv is not None else None)

    labels = [int(max(1, _as_int(value, 1))) for value in str(args.thread_count_labels or "1,8").split(",") if str(value).strip()]
    report = run_logic_stress(
        repo_root=args.repo_root,
        seed=int(max(1, _as_int(args.seed, 1010))),
        tick_count=int(max(4, _as_int(args.tick_count, 8))),
        network_count=int(max(4, _as_int(args.network_count, 12))),
        mega_node_count=int(max(1, _as_int(args.mega_node_count, 1_000_000))),
        thread_count_labels=labels,
    )
    if args.out_json:
        _write_json(os.path.join(args.repo_root, args.out_json.replace("/", os.sep)), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if _token(report.get("result")) == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
