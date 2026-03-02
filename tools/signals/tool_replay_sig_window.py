#!/usr/bin/env python3
"""SIG-7 replay-window verification helper."""

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

from tools.signals.tool_run_sig_stress import _as_int, _load_json, _run_scenario, _write_json  # noqa: E402
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


def verify_sig_replay_window(
    *,
    scenario: Mapping[str, object],
    baseline_report: Mapping[str, object],
    tick_start: int,
    tick_end: int,
    budget_envelope_id: str | None = None,
) -> dict:
    baseline = dict(baseline_report or {})
    baseline_body = dict(baseline.get("report") or baseline)
    baseline_ext = dict(baseline_body.get("extensions") or {})
    baseline_metrics = dict(baseline_body.get("metrics") or {})

    budget_id = (
        str(budget_envelope_id or "").strip()
        or str(baseline_body.get("budget_envelope_id", "")).strip()
        or "sig.envelope.standard"
    )
    tick_count = int(max(1, _as_int(baseline_body.get("tick_count", scenario.get("tick_horizon", 64)), 64)))
    replay_report = _run_scenario(
        scenario=dict(scenario or {}),
        tick_count=int(tick_count),
        budget_envelope_id=str(budget_id),
    )

    expected_window_hashes = _slice(
        baseline_ext.get("proof_hashes_per_tick"),
        start_tick=int(tick_start),
        end_tick=int(tick_end),
    )
    observed_window_hashes = _slice(
        dict(replay_report.get("extensions") or {}).get("proof_hashes_per_tick"),
        start_tick=int(tick_start),
        end_tick=int(tick_end),
    )
    expected_window_chain = canonical_sha256(expected_window_hashes)
    observed_window_chain = canonical_sha256(observed_window_hashes)

    expected_proof_hashes = dict(baseline_metrics.get("proof_hashes") or {})
    observed_proof_hashes = dict(dict(replay_report.get("metrics") or {}).get("proof_hashes") or {})
    full_proof_hash_match = expected_proof_hashes == observed_proof_hashes
    window_match = expected_window_hashes == observed_window_hashes

    result = {
        "schema_version": "1.0.0",
        "result": "complete" if (full_proof_hash_match and window_match) else "refused",
        "scenario_id": str(replay_report.get("scenario_id", "")).strip(),
        "budget_envelope_id": str(budget_id),
        "tick_window": {
            "start_tick": int(max(0, _as_int(tick_start, 0))),
            "end_tick": int(max(0, _as_int(tick_end, tick_start))),
        },
        "hashes": {
            "expected_window_chain": str(expected_window_chain),
            "observed_window_chain": str(observed_window_chain),
            "expected_full_proof_hashes_hash": canonical_sha256(expected_proof_hashes),
            "observed_full_proof_hashes_hash": canonical_sha256(observed_proof_hashes),
        },
        "matches": {
            "window_hashes_match": bool(window_match),
            "full_proof_hashes_match": bool(full_proof_hash_match),
        },
        "extensions": {
            "expected_window_count": int(len(expected_window_hashes)),
            "observed_window_count": int(len(observed_window_hashes)),
            "replay_report_fingerprint": str(replay_report.get("deterministic_fingerprint", "")),
            "baseline_report_fingerprint": str(baseline_body.get("deterministic_fingerprint", "")),
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
                "code": "refusal.sig.replay_window_hash_mismatch",
                "message": "SIG replay window verification mismatch",
                "path": "$.matches",
            }
        ],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Replay a SIG tick window and verify deterministic hashes.")
    parser.add_argument("--scenario", default="build/signals/sig_stress_scenario.json")
    parser.add_argument("--baseline-report", default="build/signals/sig_stress_report.json")
    parser.add_argument("--tick-start", type=int, default=0)
    parser.add_argument("--tick-end", type=int, default=15)
    parser.add_argument("--budget-envelope-id", default="")
    parser.add_argument("--output", default="build/signals/sig_replay_window_report.json")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()

    scenario_abs = os.path.normpath(os.path.abspath(str(args.scenario)))
    baseline_abs = os.path.normpath(os.path.abspath(str(args.baseline_report)))
    scenario = _load_json(scenario_abs)
    baseline = _load_json(baseline_abs)
    result = verify_sig_replay_window(
        scenario=scenario,
        baseline_report=baseline,
        tick_start=int(args.tick_start),
        tick_end=int(args.tick_end),
        budget_envelope_id=str(args.budget_envelope_id),
    )
    result["scenario_path"] = scenario_abs
    result["baseline_report_path"] = baseline_abs

    output = str(args.output).strip()
    if output:
        output_abs = os.path.normpath(os.path.abspath(output))
        _write_json(output_abs, result)
        result["output_path"] = output_abs

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")).strip() == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())

