#!/usr/bin/env python3
"""CHEM-4 replay-window verification helper."""

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

from tools.chem.tool_generate_chem_stress import _as_int, _read_json, _write_json  # noqa: E402
from tools.chem.tool_run_chem_stress import _envelope_defaults, run_chem_stress_scenario  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _slice(values: object, start_tick: int, end_tick: int) -> list:
    rows = list(values or [])
    start_i = int(max(0, _as_int(start_tick, 0)))
    end_i = int(max(start_i, _as_int(end_tick, start_i)))
    if not rows:
        return []
    if start_i >= len(rows):
        return []
    return list(rows[start_i : min(len(rows), end_i + 1)])


def _window_hash(values: object, start_tick: int, end_tick: int) -> str:
    return canonical_sha256(_slice(values, start_tick, end_tick))


def _tick_filtered_rows(rows: object, start_tick: int, end_tick: int, id_keys: list[str]) -> list:
    out = []
    start_i = int(max(0, _as_int(start_tick, 0)))
    end_i = int(max(start_i, _as_int(end_tick, start_i)))
    for row in list(rows or []):
        if not isinstance(row, Mapping):
            continue
        tick = int(max(0, _as_int(row.get("tick", 0), 0)))
        if tick < start_i or tick > end_i:
            continue
        out.append(dict(row))
    return sorted(
        out,
        key=lambda row: tuple(
            [int(max(0, _as_int(row.get("tick", 0), 0)))]
            + [str(row.get(str(key), "")).strip() for key in list(id_keys or [])]
        ),
    )


def verify_chem_replay_window(
    *,
    scenario: Mapping[str, object],
    baseline_report: Mapping[str, object],
    tick_start: int,
    tick_end: int,
    budget_envelope_id: str | None = None,
    max_reaction_evaluations_per_tick: int = 0,
    max_cost_units_per_tick: int = 0,
    max_model_cost_units_per_tick: int = 0,
    base_tick_stride: int = 0,
    max_emission_events_per_tick: int = 0,
) -> dict:
    baseline = dict(baseline_report or {})
    scenario_row = dict(scenario or {})
    budget_id = (
        str(budget_envelope_id or "").strip()
        or str(baseline.get("budget_envelope_id", "")).strip()
        or "chem.envelope.standard"
    )
    defaults = _envelope_defaults(str(budget_id))
    tick_count = int(max(1, _as_int(baseline.get("tick_count", scenario_row.get("tick_horizon", 64)), 64)))

    replay = run_chem_stress_scenario(
        scenario=scenario_row,
        tick_count=int(tick_count),
        budget_envelope_id=str(budget_id),
        max_reaction_evaluations_per_tick=int(max_reaction_evaluations_per_tick)
        or int(defaults["max_reaction_evaluations_per_tick"]),
        max_cost_units_per_tick=int(max_cost_units_per_tick) or int(defaults["max_cost_units_per_tick"]),
        max_model_cost_units_per_tick=int(max_model_cost_units_per_tick)
        or int(defaults["max_model_cost_units_per_tick"]),
        base_tick_stride=int(base_tick_stride) or int(defaults["base_tick_stride"]),
        max_emission_events_per_tick=int(max_emission_events_per_tick)
        or int(defaults["max_emission_events_per_tick"]),
    )

    baseline_metrics = dict(baseline.get("metrics") or {})
    replay_metrics = dict(replay.get("metrics") or {})
    baseline_ext = dict(baseline.get("extensions") or {})
    replay_ext = dict(replay.get("extensions") or {})

    baseline_window_proof = _slice(baseline_ext.get("proof_hashes_per_tick"), tick_start, tick_end)
    replay_window_proof = _slice(replay_ext.get("proof_hashes_per_tick"), tick_start, tick_end)
    proof_window_match = baseline_window_proof == replay_window_proof

    baseline_reaction_hash = canonical_sha256(
        _tick_filtered_rows(baseline_ext.get("reaction_event_rows"), tick_start, tick_end, ["event_id", "run_id"])
    )
    replay_reaction_hash = canonical_sha256(
        _tick_filtered_rows(replay_ext.get("reaction_event_rows"), tick_start, tick_end, ["event_id", "run_id"])
    )
    reaction_window_match = baseline_reaction_hash == replay_reaction_hash

    baseline_energy_hash = canonical_sha256(
        _tick_filtered_rows(baseline_ext.get("energy_ledger_rows"), tick_start, tick_end, ["entry_id", "source_id"])
    )
    replay_energy_hash = canonical_sha256(
        _tick_filtered_rows(replay_ext.get("energy_ledger_rows"), tick_start, tick_end, ["entry_id", "source_id"])
    )
    energy_window_match = baseline_energy_hash == replay_energy_hash

    baseline_emission_hash = canonical_sha256(
        _tick_filtered_rows(baseline_ext.get("emission_event_rows"), tick_start, tick_end, ["event_id", "run_id"])
    )
    replay_emission_hash = canonical_sha256(
        _tick_filtered_rows(replay_ext.get("emission_event_rows"), tick_start, tick_end, ["event_id", "run_id"])
    )
    emission_window_match = baseline_emission_hash == replay_emission_hash

    baseline_degradation_hash = canonical_sha256(
        _tick_filtered_rows(baseline_ext.get("degradation_event_rows"), tick_start, tick_end, ["run_id", "event_kind"])
    )
    replay_degradation_hash = canonical_sha256(
        _tick_filtered_rows(replay_ext.get("degradation_event_rows"), tick_start, tick_end, ["run_id", "event_kind"])
    )
    degradation_window_match = baseline_degradation_hash == replay_degradation_hash

    baseline_cost_hash = _window_hash(baseline_metrics.get("per_tick_cost_units"), tick_start, tick_end)
    replay_cost_hash = _window_hash(replay_metrics.get("per_tick_cost_units"), tick_start, tick_end)
    cost_window_match = baseline_cost_hash == replay_cost_hash

    full_proof_summary_match = dict(baseline_metrics.get("proof_hash_summary") or {}) == dict(
        replay_metrics.get("proof_hash_summary") or {}
    )

    result = {
        "schema_version": "1.0.0",
        "result": "complete"
        if (
            proof_window_match
            and reaction_window_match
            and energy_window_match
            and emission_window_match
            and degradation_window_match
            and cost_window_match
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
            "expected_reaction_window_hash": str(baseline_reaction_hash),
            "observed_reaction_window_hash": str(replay_reaction_hash),
            "expected_energy_window_hash": str(baseline_energy_hash),
            "observed_energy_window_hash": str(replay_energy_hash),
            "expected_emission_window_hash": str(baseline_emission_hash),
            "observed_emission_window_hash": str(replay_emission_hash),
            "expected_degradation_window_hash": str(baseline_degradation_hash),
            "observed_degradation_window_hash": str(replay_degradation_hash),
            "expected_cost_window_hash": str(baseline_cost_hash),
            "observed_cost_window_hash": str(replay_cost_hash),
        },
        "matches": {
            "proof_window_match": bool(proof_window_match),
            "reaction_window_match": bool(reaction_window_match),
            "energy_window_match": bool(energy_window_match),
            "emission_window_match": bool(emission_window_match),
            "degradation_window_match": bool(degradation_window_match),
            "cost_window_match": bool(cost_window_match),
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
                "code": "refusal.chem.replay_window_hash_mismatch",
                "message": "CHEM replay window hash mismatch",
                "path": "$.matches",
            }
        ],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Replay CHEM tick window and verify deterministic hashes.")
    parser.add_argument("--scenario", default="build/chem/chem_stress_scenario.json")
    parser.add_argument("--baseline-report", default="build/chem/chem_stress_report.json")
    parser.add_argument("--tick-start", type=int, default=0)
    parser.add_argument("--tick-end", type=int, default=15)
    parser.add_argument("--budget-envelope-id", default="")
    parser.add_argument("--max-reaction-evaluations-per-tick", type=int, default=0)
    parser.add_argument("--max-cost-units-per-tick", type=int, default=0)
    parser.add_argument("--max-model-cost-units-per-tick", type=int, default=0)
    parser.add_argument("--base-tick-stride", type=int, default=0)
    parser.add_argument("--max-emission-events-per-tick", type=int, default=0)
    parser.add_argument("--output", default="build/chem/chem_replay_window_report.json")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()

    scenario_abs = os.path.normpath(os.path.abspath(str(args.scenario)))
    baseline_abs = os.path.normpath(os.path.abspath(str(args.baseline_report)))
    scenario = _read_json(scenario_abs)
    baseline = _read_json(baseline_abs)
    result = verify_chem_replay_window(
        scenario=scenario if isinstance(scenario, Mapping) else {},
        baseline_report=baseline if isinstance(baseline, Mapping) else {},
        tick_start=int(args.tick_start),
        tick_end=int(args.tick_end),
        budget_envelope_id=str(args.budget_envelope_id),
        max_reaction_evaluations_per_tick=int(args.max_reaction_evaluations_per_tick),
        max_cost_units_per_tick=int(args.max_cost_units_per_tick),
        max_model_cost_units_per_tick=int(args.max_model_cost_units_per_tick),
        base_tick_stride=int(args.base_tick_stride),
        max_emission_events_per_tick=int(args.max_emission_events_per_tick),
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
