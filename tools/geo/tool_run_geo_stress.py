#!/usr/bin/env python3
"""Run the deterministic GEO-10 stress harness and verify repeated-run stability."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.geo.geo10_stress_runtime import (  # noqa: E402
    DEFAULT_GEO10_SEED,
    DEFAULT_REPORT_REL,
    load_geo_stress_scenario,
    verify_geo_stress_scenario,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic GEO-10 stress verification.")
    parser.add_argument("--scenario", default="")
    parser.add_argument("--seed", type=int, default=DEFAULT_GEO10_SEED)
    parser.add_argument("--output", default=DEFAULT_REPORT_REL)
    return parser


def main() -> int:
    args = _parser().parse_args()
    scenario = load_geo_stress_scenario(str(args.scenario or "").strip())
    report = verify_geo_stress_scenario(
        scenario,
        seed=int(args.seed),
    )
    output_abs = os.path.normpath(os.path.abspath(str(args.output)))
    os.makedirs(os.path.dirname(output_abs), exist_ok=True)
    with open(output_abs, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")
    summary = {
        "output_path": output_abs,
        "result": str(report.get("result", "")),
        "scenario_id": str(report.get("scenario_id", "")),
        "suite_count": int(len(list(report.get("topology_suite_reports") or []))),
        "cross_platform_determinism_hash": str(
            dict(report.get("proof_summary") or {}).get("cross_platform_determinism_hash", "")
        ),
        "stable_across_repeated_runs": bool(report.get("stable_across_repeated_runs", False)),
        "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
