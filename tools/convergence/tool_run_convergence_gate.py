#!/usr/bin/env python3
"""Run CONVERGENCE-GATE-0 in deterministic order."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.convergence.convergence_gate_common import run_convergence_gate  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--skip-cross-platform", action="store_true")
    parser.add_argument("--prefer-cached-heavy", action="store_true")
    parser.add_argument("--include-dist-verify", action="store_true")
    args = parser.parse_args(argv)

    report = run_convergence_gate(
        os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT))),
        skip_cross_platform=bool(args.skip_cross_platform),
        prefer_cached_heavy=bool(args.prefer_cached_heavy),
        include_dist_verify=bool(args.include_dist_verify),
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
