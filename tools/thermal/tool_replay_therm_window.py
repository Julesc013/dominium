#!/usr/bin/env python3
"""THERM-5 replay-window verification helper."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.thermal.tool_generate_therm_stress_scenario import _as_int, _write_json  # noqa: E402
from tools.thermal.tool_run_therm_stress import _envelope_defaults, _load_json, run_therm_stress_scenario  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _slice(values, start_tick, end_tick):
    rows = list(values or [])
    start_i = int(max(0, _as_int(start_tick, 0)))
    end_i = int(max(start_i, _as_int(end_tick, start_i)))
    if not rows:
        return []
    if start_i >= len(rows):
        return []
    return list(rows[start_i : min(len(rows), end_i + 1)])


def _window_hash(values, start_tick, end_tick):
    return canonical_sha256(_slice(values, start_tick, end_tick))


def verify_therm_replay_window(
    *,
    scenario,
    baseline_report,
    tick_start,
    tick_end,
    budget_envelope_id=None,
    max_cost_units_per_tick=0,
    max_processed_edges_per_network=4096,
    max_model_cost_units_per_network=0,
    base_t1_tick_stride=0,
    max_fire_spread_per_tick=0,
    ambient_temperature=20,
):
    baseline = dict(baseline_report or {})
    scenario_row = dict(scenario or {})

    budget_id = (
        str(budget_envelope_id or "").strip()
        or str(baseline.get("budget_envelope_id", "")).strip()
        or "therm.envelope.standard"
    )
    defaults = _envelope_defaults(str(budget_id))
    tick_count = int(max(1, _as_int(baseline.get("tick_count", scenario_row.get("tick_horizon", 64)), 64)))

    replay = run_therm_stress_scenario(
        scenario=scenario_row,
        tick_count=int(tick_count),
        budget_envelope_id=str(budget_id),
        max_cost_units_per_tick=int(max_cost_units_per_tick) or int(defaults["max_cost_units_per_tick"]),
        max_processed_edges_per_network=int(max_processed_edges_per_network),
        max_model_cost_units_per_network=int(max_model_cost_units_per_network) or int(defaults["max_model_cost_units_per_network"]),
        base_t1_tick_stride=int(base_t1_tick_stride) or int(defaults["base_t1_tick_stride"]),
        max_fire_spread_per_tick=int(max_fire_spread_per_tick) or int(defaults["max_fire_spread_per_tick"]),
        ambient_temperature=int(ambient_temperature),
    )

    baseline_metrics = dict(baseline.get("metrics") or {})
    replay_metrics = dict(replay.get("metrics") or {})
    baseline_ext = dict(baseline.get("extensions") or {})
    replay_ext = dict(replay.get("extensions") or {})

    baseline_window_proof = _slice(baseline_ext.get("proof_hashes_per_tick"), tick_start, tick_end)
    replay_window_proof = _slice(replay_ext.get("proof_hashes_per_tick"), tick_start, tick_end)

    baseline_temp_hash = _window_hash(baseline_metrics.get("max_temperature_per_tick"), tick_start, tick_end)
    replay_temp_hash = _window_hash(replay_metrics.get("max_temperature_per_tick"), tick_start, tick_end)

    baseline_event_hash = canonical_sha256(
        {
            "fire": _slice(baseline_metrics.get("fire_event_counts_per_tick"), tick_start, tick_end),
            "overtemp": _slice(baseline_metrics.get("overtemp_trip_counts_per_tick"), tick_start, tick_end),
        }
    )
    replay_event_hash = canonical_sha256(
        {
            "fire": _slice(replay_metrics.get("fire_event_counts_per_tick"), tick_start, tick_end),
            "overtemp": _slice(replay_metrics.get("overtemp_trip_counts_per_tick"), tick_start, tick_end),
        }
    )

    baseline_degrade_hash = canonical_sha256(
        _slice(
            [
                dict(row)
                for row in list(baseline_ext.get("thermal_degradation_event_rows") or [])
                if isinstance(row, dict)
            ],
            tick_start,
            tick_end,
        )
    )
    replay_degrade_hash = canonical_sha256(
        _slice(
            [
                dict(row)
                for row in list(replay_ext.get("thermal_degradation_event_rows") or [])
                if isinstance(row, dict)
            ],
            tick_start,
            tick_end,
        )
    )

    proof_window_match = baseline_window_proof == replay_window_proof
    temp_window_match = baseline_temp_hash == replay_temp_hash
    event_window_match = baseline_event_hash == replay_event_hash
    degrade_window_match = baseline_degrade_hash == replay_degrade_hash
    full_proof_summary_match = dict(baseline_metrics.get("proof_hash_summary") or {}) == dict(replay_metrics.get("proof_hash_summary") or {})

    result = {
        "schema_version": "1.0.0",
        "result": "complete"
        if (
            proof_window_match
            and temp_window_match
            and event_window_match
            and degrade_window_match
            and full_proof_summary_match
            and str(replay.get("result", "")).strip() == "complete"
        )
        else "refused",
        "scenario_id": str(scenario_row.get("scenario_id", "")).strip(),
        "budget_envelope_id": str(budget_id),
        "tick_window": {
            "start_tick": int(max(0, _as_int(tick_start, 0))),
            "end_tick": int(max(_as_int(tick_start, 0), _as_int(tick_end, tick_start))),
        },
        "hashes": {
            "expected_window_proof_chain": canonical_sha256(list(baseline_window_proof)),
            "observed_window_proof_chain": canonical_sha256(list(replay_window_proof)),
            "expected_temperature_window_hash": str(baseline_temp_hash),
            "observed_temperature_window_hash": str(replay_temp_hash),
            "expected_event_window_hash": str(baseline_event_hash),
            "observed_event_window_hash": str(replay_event_hash),
            "expected_degradation_window_hash": str(baseline_degrade_hash),
            "observed_degradation_window_hash": str(replay_degrade_hash),
        },
        "matches": {
            "proof_window_match": bool(proof_window_match),
            "temperature_window_match": bool(temp_window_match),
            "event_window_match": bool(event_window_match),
            "degradation_window_match": bool(degrade_window_match),
            "full_proof_summary_match": bool(full_proof_summary_match),
            "replay_completed": bool(str(replay.get("result", "")).strip() == "complete"),
        },
        "extensions": {
            "baseline_report_fingerprint": str(baseline.get("deterministic_fingerprint", "")),
            "replay_report_fingerprint": str(replay.get("deterministic_fingerprint", "")),
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
                "code": "refusal.therm.replay_window_hash_mismatch",
                "message": "THERM replay window hash mismatch",
                "path": "$.matches",
            }
        ],
    }


def _parser():
    parser = argparse.ArgumentParser(description="Replay THERM tick window and verify deterministic hashes.")
    parser.add_argument("--scenario", default="build/thermal/therm_stress_scenario.json")
    parser.add_argument("--baseline-report", default="build/thermal/therm_stress_report.json")
    parser.add_argument("--tick-start", type=int, default=0)
    parser.add_argument("--tick-end", type=int, default=15)
    parser.add_argument("--budget-envelope-id", default="")
    parser.add_argument("--max-cost-units-per-tick", type=int, default=0)
    parser.add_argument("--max-processed-edges-per-network", type=int, default=4096)
    parser.add_argument("--max-model-cost-units-per-network", type=int, default=0)
    parser.add_argument("--base-t1-tick-stride", type=int, default=0)
    parser.add_argument("--max-fire-spread-per-tick", type=int, default=0)
    parser.add_argument("--ambient-temperature", type=int, default=20)
    parser.add_argument("--output", default="build/thermal/therm_replay_window_report.json")
    return parser


def main():
    parser = _parser()
    args = parser.parse_args()

    scenario_abs = os.path.normpath(os.path.abspath(str(args.scenario)))
    baseline_abs = os.path.normpath(os.path.abspath(str(args.baseline_report)))
    scenario = _load_json(scenario_abs)
    baseline = _load_json(baseline_abs)
    result = verify_therm_replay_window(
        scenario=scenario,
        baseline_report=baseline,
        tick_start=int(args.tick_start),
        tick_end=int(args.tick_end),
        budget_envelope_id=str(args.budget_envelope_id),
        max_cost_units_per_tick=int(args.max_cost_units_per_tick),
        max_processed_edges_per_network=int(args.max_processed_edges_per_network),
        max_model_cost_units_per_network=int(args.max_model_cost_units_per_network),
        base_t1_tick_stride=int(args.base_t1_tick_stride),
        max_fire_spread_per_tick=int(args.max_fire_spread_per_tick),
        ambient_temperature=int(args.ambient_temperature),
    )
    output_abs = os.path.normpath(os.path.abspath(str(args.output)))
    _write_json(output_abs, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")).strip() == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
