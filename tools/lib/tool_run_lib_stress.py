#!/usr/bin/env python3
"""Run the deterministic LIB-7 library stress harness."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.lib.lib_stress_common import DEFAULT_BASELINE_REL, DEFAULT_LIB7_SEED, DEFAULT_WORKSPACE_REL, run_lib_stress, write_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the LIB-7 deterministic library stress harness.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--out-root", default=DEFAULT_WORKSPACE_REL.replace("\\", "/"))
    parser.add_argument("--seed", default=str(DEFAULT_LIB7_SEED))
    parser.add_argument("--slash-mode", default="forward", choices=("forward", "backward"))
    parser.add_argument("--baseline-out", default="")
    parser.add_argument("--report-out", default="")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    out_root = os.path.normpath(os.path.abspath(os.path.join(repo_root, str(args.out_root or DEFAULT_WORKSPACE_REL))))
    baseline_out = str(args.baseline_out or "").strip()
    report = run_lib_stress(
        repo_root=repo_root,
        out_root=out_root,
        seed=int(str(args.seed or DEFAULT_LIB7_SEED).strip() or DEFAULT_LIB7_SEED),
        slash_mode=str(args.slash_mode or "forward").strip() or "forward",
        baseline_out=(os.path.normpath(os.path.abspath(os.path.join(repo_root, baseline_out))) if baseline_out else ""),
    )
    report_out = str(args.report_out or "").strip()
    if report_out:
        write_json(os.path.normpath(os.path.abspath(os.path.join(repo_root, report_out))), report)
    elif not baseline_out:
        default_report = os.path.join(out_root, "lib_stress_report.json")
        write_json(default_report, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
