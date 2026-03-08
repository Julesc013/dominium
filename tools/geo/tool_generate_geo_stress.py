#!/usr/bin/env python3
"""Generate deterministic GEO-10 stress scenario payloads."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.geo.geo10_stress_common import (  # noqa: E402
    DEFAULT_GEO10_SEED,
    DEFAULT_OUTPUT_REL,
    _as_int,
    generate_geo_stress_scenario,
    write_json,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate deterministic GEO-10 stress scenario.")
    parser.add_argument("--seed", type=int, default=DEFAULT_GEO10_SEED)
    parser.add_argument("--include-cctv", choices=("true", "false"), default="true")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_REL)
    return parser


def main() -> int:
    args = _parser().parse_args()
    scenario = generate_geo_stress_scenario(
        seed=int(args.seed),
        include_cctv=str(args.include_cctv).strip().lower() != "false",
    )
    output_abs = os.path.normpath(os.path.abspath(str(args.output)))
    write_json(output_abs, scenario)
    summary = {
        "output_path": output_abs,
        "scenario_id": str(scenario.get("scenario_id", "")),
        "suite_count": int(len(list(scenario.get("topology_suites") or []))),
        "scenario_seed": int(_as_int(scenario.get("scenario_seed", 0), 0)),
        "deterministic_fingerprint": str(scenario.get("deterministic_fingerprint", "")),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
