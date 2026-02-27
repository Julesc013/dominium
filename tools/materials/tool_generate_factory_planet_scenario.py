#!/usr/bin/env python3
"""Generate deterministic MAT-10 factory-planet stress scenarios."""

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

from src.materials.performance.mat_scale_engine import (  # noqa: E402
    DEFAULT_MAT_SCALE_COST_MODEL,
    default_factory_planet_scenario,
    normalize_mat_scale_cost_model,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _ensure_dir(path: str) -> None:
    if path and not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def _write_json(path: str, payload: Dict[str, object]) -> None:
    parent = os.path.dirname(path)
    _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def run_generate(args: argparse.Namespace) -> dict:
    scenario = default_factory_planet_scenario(
        seed=int(args.seed),
        factory_complex_count=int(args.factory_complex_count),
        logistics_node_count=int(args.logistics_node_count),
        active_project_count=int(args.active_project_count),
        player_count=int(args.player_count),
    )
    scenario["multiplayer_policy_id"] = str(args.multiplayer_policy_id).strip() or str(
        scenario.get("multiplayer_policy_id", "policy.net.server_authoritative")
    )
    scenario["arbitration_policy_id"] = str(args.arbitration_policy_id).strip() or str(
        scenario.get("arbitration_policy_id", "arb.equal_share.deterministic")
    )
    scenario["cost_model"] = normalize_mat_scale_cost_model(DEFAULT_MAT_SCALE_COST_MODEL)
    scenario["deterministic_fingerprint"] = canonical_sha256(
        dict(scenario, deterministic_fingerprint="")
    )

    output_path = os.path.normpath(os.path.abspath(str(args.output)))
    _write_json(output_path, scenario)
    return {
        "result": "complete",
        "output_path": output_path,
        "scenario_id": str(scenario.get("scenario_id", "")),
        "deterministic_fingerprint": str(scenario.get("deterministic_fingerprint", "")),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate deterministic MAT-10 factory-planet stress scenario payload."
    )
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--seed", type=int, default=424242)
    parser.add_argument("--factory-complex-count", type=int, default=128)
    parser.add_argument("--logistics-node-count", type=int, default=768)
    parser.add_argument("--active-project-count", type=int, default=512)
    parser.add_argument("--player-count", type=int, default=256)
    parser.add_argument("--arbitration-policy-id", default="arb.equal_share.deterministic")
    parser.add_argument("--multiplayer-policy-id", default="policy.net.server_authoritative")
    parser.add_argument(
        "--output",
        default="build/mat10/scenario.factory_planet.default.json",
        help="output scenario JSON path",
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
    result = run_generate(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
