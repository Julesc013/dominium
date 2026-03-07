#!/usr/bin/env python3
"""Run a deterministic LOGIC-6 compile/collapse stress scenario and summarize compiled parity."""

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

from src.logic.signal import canonical_signal_hash
from tools.logic.tool_replay_compiled_logic_window import replay_compiled_logic_window_from_payload
from tools.logic.tool_replay_logic_window import _write_json
from tools.logic.tool_run_logic_eval_stress import build_logic_eval_stress_scenario
from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _token(value: object) -> str:
    return str(value or "").strip()


def run_logic_compile_stress(
    *,
    repo_root: str,
    element_pairs: int = 24,
    tick_count: int = 8,
) -> dict:
    scenario = build_logic_eval_stress_scenario(
        repo_root=repo_root,
        element_pairs=element_pairs,
        tick_count=tick_count,
    )
    report = replay_compiled_logic_window_from_payload(repo_root=repo_root, payload=scenario)
    if _token(report.get("result")) != "complete":
        return report

    compiled_report = _as_map(report.get("compiled_report"))
    logic_eval_state = _as_map(compiled_report.get("final_logic_eval_state"))
    eval_rows = [
        dict(row)
        for row in list(logic_eval_state.get("logic_eval_record_rows") or [])
        if isinstance(row, Mapping)
    ]
    runtime_rows = [
        dict(row)
        for row in list(logic_eval_state.get("logic_network_runtime_state_rows") or [])
        if isinstance(row, Mapping)
    ]
    return {
        "result": "complete",
        "scenario_id": scenario["scenario_id"],
        "network_id": "net.logic.eval.stress",
        "element_pairs": int(scenario["element_pairs"]),
        "element_count": int(scenario["element_pairs"]) * 2,
        "tick_count": int(scenario["tick_count"]),
        "compiled_type_ids": list(report.get("compiled_type_ids") or []),
        "compiled_model_ids": list(report.get("compiled_model_ids") or []),
        "compiled_path_observed": bool(report.get("compiled_path_observed", False)),
        "signals_match": bool(report.get("signals_match", False)),
        "states_match": bool(report.get("states_match", False)),
        "tick_signal_match": bool(report.get("tick_signal_match", False)),
        "ticks_completed": int(len(eval_rows)),
        "runtime_record_count": int(len(runtime_rows)),
        "max_elements_evaluated": int(
            max((int(row.get("elements_evaluated_count", 0) or 0) for row in eval_rows), default=0)
        ),
        "max_compute_units_used": int(
            max((int(row.get("compute_units_used", 0) or 0) for row in eval_rows), default=0)
        ),
        "final_signal_hash": _token(report.get("compiled_final_signal_hash") or report.get("final_signal_hash")),
        "final_signal_store_hash": canonical_signal_hash(state=compiled_report.get("final_signal_store_state")),
        "compile_result_hash_chain": _token(report.get("compile_result_hash_chain")),
        "compiled_model_hash_chain": _token(report.get("compiled_model_hash_chain")),
        "equivalence_proof_hash_chain": _token(report.get("equivalence_proof_hash_chain")),
        "logic_compile_policy_hash_chain": _token(report.get("logic_compile_policy_hash_chain")),
        "forced_expand_event_hash_chain": _token(report.get("forced_expand_event_hash_chain")),
        "deterministic_fingerprint": canonical_sha256(
            {
                "scenario_id": scenario["scenario_id"],
                "compiled_type_ids": list(report.get("compiled_type_ids") or []),
                "compiled_model_ids": list(report.get("compiled_model_ids") or []),
                "signals_match": bool(report.get("signals_match", False)),
                "states_match": bool(report.get("states_match", False)),
                "tick_signal_match": bool(report.get("tick_signal_match", False)),
                "final_signal_hash": _token(report.get("compiled_final_signal_hash") or report.get("final_signal_hash")),
                "compiled_model_hash_chain": _token(report.get("compiled_model_hash_chain")),
                "equivalence_proof_hash_chain": _token(report.get("equivalence_proof_hash_chain")),
                "logic_compile_policy_hash_chain": _token(report.get("logic_compile_policy_hash_chain")),
                "forced_expand_event_hash_chain": _token(report.get("forced_expand_event_hash_chain")),
            }
        ),
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--element-pairs", type=int, default=24)
    parser.add_argument("--tick-count", type=int, default=8)
    parser.add_argument("--out-json", default="")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = run_logic_compile_stress(
        repo_root=args.repo_root,
        element_pairs=int(args.element_pairs),
        tick_count=int(args.tick_count),
    )
    if args.out_json:
        _write_json(os.path.join(args.repo_root, args.out_json.replace("/", os.sep)), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if _token(report.get("result")) == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
