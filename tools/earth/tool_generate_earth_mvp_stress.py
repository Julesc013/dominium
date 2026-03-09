#!/usr/bin/env python3
"""Generate deterministic EARTH-9 MVP stress scenario payloads."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.earth.earth9_stress_common import (  # noqa: E402
    DEFAULT_EARTH9_SEED,
    DEFAULT_SCENARIO_REL,
    generate_earth_mvp_stress_scenario,
    write_json,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate deterministic EARTH-9 MVP stress scenario.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--seed", type=int, default=DEFAULT_EARTH9_SEED)
    parser.add_argument("--output", default=DEFAULT_SCENARIO_REL)
    return parser


def main() -> int:
    args = _parser().parse_args()
    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    scenario = generate_earth_mvp_stress_scenario(repo_root=repo_root, seed=int(args.seed))
    output_abs = os.path.normpath(os.path.abspath(str(args.output)))
    write_json(output_abs, scenario)
    summary = {
        "output_path": output_abs,
        "scenario_id": str(scenario.get("scenario_id", "")),
        "scenario_seed": int(scenario.get("scenario_seed", 0) or 0),
        "waypoint_count": int(len(list(scenario.get("waypoints") or []))),
        "deterministic_fingerprint": str(scenario.get("deterministic_fingerprint", "")),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
