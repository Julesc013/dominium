#!/usr/bin/env python3
"""Run deterministic MAT-10 stress harness with cost/degradation outputs."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from materials.performance.mat_scale_engine import (  # noqa: E402
    default_factory_planet_scenario,
    run_stress_simulation,
)


def _ensure_dir(path: str) -> None:
    if path and not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_json(path: str, payload: Dict[str, object]) -> None:
    parent = os.path.dirname(path)
    _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _scenario_from_args(args: argparse.Namespace) -> tuple[dict, dict]:
    if str(args.scenario_file).strip():
        scenario_path = os.path.normpath(os.path.abspath(str(args.scenario_file)))
        payload = _read_json(scenario_path)
        if not payload:
            return {}, {
                "result": "refused",
                "errors": [
                    {
                        "code": "refusal.mat_scale.scenario_invalid",
                        "message": "scenario-file missing or invalid JSON object",
                        "path": "$.scenario_file",
                    }
                ],
            }
        return payload, {}
    scenario = default_factory_planet_scenario(
        seed=int(args.seed),
        factory_complex_count=int(args.factory_complex_count),
        logistics_node_count=int(args.logistics_node_count),
        active_project_count=int(args.active_project_count),
        player_count=int(args.player_count),
    )
    return scenario, {}


def run_harness(args: argparse.Namespace) -> dict:
    scenario, err = _scenario_from_args(args)
    if err:
        return err
    tick_count = max(0, int(args.tick_count))
    if tick_count <= 0:
        return {
            "result": "refused",
            "errors": [
                {
                    "code": "refusal.mat_scale.tick_count_invalid",
                    "message": "tick-count must be positive",
                    "path": "$.tick_count",
                }
            ],
        }
    report = run_stress_simulation(
        scenario_row=scenario,
        tick_count=tick_count,
        budget_envelope_id=str(args.budget_envelope_id).strip() or None,
        arbitration_policy_id=str(args.arbitration_policy_id).strip() or None,
        multiplayer_policy_id=str(args.multiplayer_policy_id).strip() or None,
        strict_budget=bool(args.strict_budget),
    )
    out = {
        "result": "complete",
        "stress_report": report,
        "summary": {
            "scenario_id": str(report.get("scenario_id", "")),
            "tick_count": int(report.get("tick_count", 0) or 0),
            "bounded": bool(report.get("bounded", False)),
            "degradation_event_count": len(list(report.get("degradation_events") or [])),
            "hash_anchor_count": len(list(report.get("hash_anchor_stream") or [])),
            "inspection_cache_hit_rate_permille": int(
                (dict(report.get("inspection_cache_summary") or {}).get("hit_rate_permille", 0) or 0)
            ),
        },
    }
    output_path = str(args.output).strip()
    if output_path:
        normalized = os.path.normpath(os.path.abspath(output_path))
        _write_json(normalized, out)
        out["output_path"] = normalized
    return out


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic MAT-10 stress harness.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--scenario-file", default="")
    parser.add_argument("--seed", type=int, default=424242)
    parser.add_argument("--factory-complex-count", type=int, default=128)
    parser.add_argument("--logistics-node-count", type=int, default=768)
    parser.add_argument("--active-project-count", type=int, default=512)
    parser.add_argument("--player-count", type=int, default=256)
    parser.add_argument("--tick-count", type=int, default=64)
    parser.add_argument("--budget-envelope-id", default="budget.factory_planet.default")
    parser.add_argument("--arbitration-policy-id", default="arb.equal_share.deterministic")
    parser.add_argument("--multiplayer-policy-id", default="policy.net.server_authoritative")
    parser.add_argument("--strict-budget", action="store_true")
    parser.add_argument(
        "--output",
        default="build/mat10/stress_report.default.json",
        help="optional output JSON path",
    )
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()
    repo_root = (
        os.path.normpath(os.path.abspath(str(args.repo_root)))
        if str(args.repo_root).strip()
        else REPO_ROOT_HINT
    )
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    result = run_harness(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
