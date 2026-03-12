#!/usr/bin/env python3
"""Run the deterministic ARCH-AUDIT-0 report and write canonical artifacts."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.audit.arch_audit_common import (  # noqa: E402
    DEFAULT_BASELINE_DOC_REL,
    DEFAULT_REPORT_JSON_REL,
    DEFAULT_REPORT_MD_REL,
    load_json_if_present,
    run_arch_audit,
    write_arch_audit_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--report-path", default=DEFAULT_REPORT_MD_REL)
    parser.add_argument("--json-path", default=DEFAULT_REPORT_JSON_REL)
    parser.add_argument("--baseline-path", default="")
    parser.add_argument("--prefer-cached", action="store_true")
    args = parser.parse_args(argv)

    report = {}
    if bool(args.prefer_cached):
        report = load_json_if_present(args.repo_root, str(args.json_path))
    if not report:
        report = run_arch_audit(args.repo_root)
    written = write_arch_audit_outputs(
        args.repo_root,
        report=report,
        report_path=str(args.report_path),
        json_path=str(args.json_path),
        baseline_path=str(args.baseline_path),
    )
    payload = dict(report)
    payload["written_outputs"] = written
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
