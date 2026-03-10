#!/usr/bin/env python3
"""Run the deterministic EARTH-9 MVP stress harness."""

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
    DEFAULT_REPORT_REL,
    load_earth_mvp_stress_scenario,
    verify_earth_mvp_stress_scenario,
    write_json,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic EARTH-9 MVP stress validation.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--scenario", default="")
    parser.add_argument("--seed", type=int, default=DEFAULT_EARTH9_SEED)
    parser.add_argument("--output-path", default=DEFAULT_REPORT_REL)
    return parser


def main() -> int:
    args = _parser().parse_args()
    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    scenario = load_earth_mvp_stress_scenario(
        repo_root=repo_root,
        scenario_path=str(args.scenario or "").strip(),
        seed=int(args.seed),
    )
    report = verify_earth_mvp_stress_scenario(
        repo_root=repo_root,
        scenario=scenario,
        seed=int(args.seed),
    )
    output_path = str(args.output_path or "").strip()
    if output_path:
        write_json(os.path.normpath(os.path.abspath(output_path)), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
