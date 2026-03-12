#!/usr/bin/env python3
"""Run the deterministic MVP stress orchestrator and write stress artifacts."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.mvp.stress_gate_common import (  # noqa: E402
    DEFAULT_HASHES_REL,
    DEFAULT_MVP_STRESS_SEED,
    DEFAULT_REPORT_REL,
    maybe_load_cached_mvp_stress_report,
    run_all_mvp_stress,
    write_mvp_stress_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--seed", type=int, default=DEFAULT_MVP_STRESS_SEED)
    parser.add_argument("--report-path", default=DEFAULT_REPORT_REL)
    parser.add_argument("--hashes-path", default=DEFAULT_HASHES_REL)
    parser.add_argument("--prefer-cached", action="store_true")
    args = parser.parse_args(argv)

    report = {}
    if bool(args.prefer_cached):
        report = maybe_load_cached_mvp_stress_report(
            args.repo_root,
            report_path=str(args.report_path),
        )
    if not report:
        report = run_all_mvp_stress(args.repo_root, seed=int(args.seed))

    written = write_mvp_stress_outputs(
        args.repo_root,
        report=report,
        report_path=str(args.report_path),
        hashes_path=str(args.hashes_path),
    )
    payload = dict(report)
    payload["written_outputs"] = written
    print(json.dumps(payload, indent=2, sort_keys=True))
    report_result = str(report.get("result", "")).strip()
    if not report_result and isinstance(report.get("assertions"), dict):
        assertions = dict(report.get("assertions") or {})
        if all(bool(assertions.get(key, False)) for key in ("all_suites_passed", "cross_thread_hash_match", "no_unexpected_refusals", "suite_order_deterministic")):
            report_result = "complete"
    return 0 if report_result == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
