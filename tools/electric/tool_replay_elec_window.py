#!/usr/bin/env python3
"""ELEC-5 replay-window verification helper."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.electric.tool_generate_elec_stress_scenario import _as_int, _write_json  # noqa: E402
from tools.electric.tool_run_elec_stress import _load_json, run_elec_stress_scenario  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _slice(rows: object, start_tick: int, end_tick: int) -> list:
    values = list(rows or [])
    start_i = int(max(0, _as_int(start_tick, 0)))
    end_i = int(max(start_i, _as_int(end_tick, start_i)))
    if not values:
        return []
    if start_i >= len(values):
        return []
    return list(values[start_i : min(len(values), end_i + 1)])


def verify_elec_replay_window(
    *,
    scenario: Mapping[str, object],
    baseline_report: Mapping[str, object],
    tick_start: int,
    tick_end: int,
    budget_envelope_id: str | None = None,
    max_network_solves_per_tick: int = 8,
    max_edges_per_network: int = 4096,
    max_fault_evals_per_tick: int = 4096,
    max_trip_actions_per_tick: int = 4096,
    cascade_max_iterations: int = 4,
) -> dict:
    baseline = dict(baseline_report or {})
    scenario_row = dict(scenario or {})
    budget_id = (
        str(budget_envelope_id or "").strip()
        or str(baseline.get("budget_envelope_id", "")).strip()
        or "elec.envelope.standard"
    )
    tick_count = int(max(1, _as_int(baseline.get("tick_count", scenario_row.get("tick_horizon", 64)), 64)))

    replay = run_elec_stress_scenario(
        scenario=scenario_row,
        tick_count=int(tick_count),
        budget_envelope_id=str(budget_id),
        max_network_solves_per_tick=int(max_network_solves_per_tick),
        max_edges_per_network=int(max_edges_per_network),
        max_fault_evals_per_tick=int(max_fault_evals_per_tick),
        max_trip_actions_per_tick=int(max_trip_actions_per_tick),
        cascade_max_iterations=int(cascade_max_iterations),
    )

    baseline_proof_hashes = _slice(
        dict(baseline.get("extensions") or {}).get("proof_hashes_per_tick"),
        int(tick_start),
        int(tick_end),
    )
    replay_proof_hashes = _slice(
        dict(replay.get("extensions") or {}).get("proof_hashes_per_tick"),
        int(tick_start),
        int(tick_end),
    )
    expected_window_chain = canonical_sha256(list(baseline_proof_hashes))
    observed_window_chain = canonical_sha256(list(replay_proof_hashes))
    full_match = (
        dict(baseline.get("metrics") or {}).get("proof_hash_summary")
        == dict(replay.get("metrics") or {}).get("proof_hash_summary")
    )
    window_match = baseline_proof_hashes == replay_proof_hashes

    result = {
        "schema_version": "1.0.0",
        "result": "complete" if (window_match and full_match and str(replay.get("result", "")).strip() == "complete") else "refused",
        "scenario_id": str(scenario_row.get("scenario_id", "")).strip(),
        "budget_envelope_id": str(budget_id),
        "tick_window": {
            "start_tick": int(max(0, _as_int(tick_start, 0))),
            "end_tick": int(max(int(tick_start), _as_int(tick_end, tick_start))),
        },
        "hashes": {
            "expected_window_chain": str(expected_window_chain),
            "observed_window_chain": str(observed_window_chain),
            "expected_full_proof_hash_summary_hash": canonical_sha256(dict(baseline.get("metrics") or {}).get("proof_hash_summary") or {}),
            "observed_full_proof_hash_summary_hash": canonical_sha256(dict(replay.get("metrics") or {}).get("proof_hash_summary") or {}),
        },
        "matches": {
            "window_hashes_match": bool(window_match),
            "full_proof_summary_match": bool(full_match),
            "replay_completed": bool(str(replay.get("result", "")).strip() == "complete"),
        },
        "extensions": {
            "baseline_report_fingerprint": str(baseline.get("deterministic_fingerprint", "")),
            "replay_report_fingerprint": str(replay.get("deterministic_fingerprint", "")),
            "expected_window_count": int(len(baseline_proof_hashes)),
            "observed_window_count": int(len(replay_proof_hashes)),
        },
        "deterministic_fingerprint": "",
    }
    seed = dict(result)
    seed["deterministic_fingerprint"] = ""
    result["deterministic_fingerprint"] = canonical_sha256(seed)
    if str(result.get("result", "")).strip() == "complete":
        return result
    return {
        **result,
        "errors": [
            {
                "code": "refusal.elec.replay_window_hash_mismatch",
                "message": "ELEC replay window hash mismatch",
                "path": "$.matches",
            }
        ],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Replay ELEC tick window and verify deterministic hashes.")
    parser.add_argument("--scenario", default="build/electric/elec_stress_scenario.json")
    parser.add_argument("--baseline-report", default="build/electric/elec_stress_report.json")
    parser.add_argument("--tick-start", type=int, default=0)
    parser.add_argument("--tick-end", type=int, default=15)
    parser.add_argument("--budget-envelope-id", default="")
    parser.add_argument("--max-network-solves-per-tick", type=int, default=8)
    parser.add_argument("--max-edges-per-network", type=int, default=4096)
    parser.add_argument("--max-fault-evals-per-tick", type=int, default=4096)
    parser.add_argument("--max-trip-actions-per-tick", type=int, default=4096)
    parser.add_argument("--cascade-max-iterations", type=int, default=4)
    parser.add_argument("--output", default="build/electric/elec_replay_window_report.json")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()

    scenario_abs = os.path.normpath(os.path.abspath(str(args.scenario)))
    baseline_abs = os.path.normpath(os.path.abspath(str(args.baseline_report)))
    scenario = _load_json(scenario_abs)
    baseline = _load_json(baseline_abs)
    result = verify_elec_replay_window(
        scenario=scenario,
        baseline_report=baseline,
        tick_start=int(args.tick_start),
        tick_end=int(args.tick_end),
        budget_envelope_id=str(args.budget_envelope_id),
        max_network_solves_per_tick=int(args.max_network_solves_per_tick),
        max_edges_per_network=int(args.max_edges_per_network),
        max_fault_evals_per_tick=int(args.max_fault_evals_per_tick),
        max_trip_actions_per_tick=int(args.max_trip_actions_per_tick),
        cascade_max_iterations=int(args.cascade_max_iterations),
    )
    result["scenario_path"] = scenario_abs
    result["baseline_report_path"] = baseline_abs
    output_abs = os.path.normpath(os.path.abspath(str(args.output)))
    _write_json(output_abs, result)
    result["output_path"] = output_abs
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")).strip() == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
