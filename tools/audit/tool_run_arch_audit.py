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


from tools.import_bridge import install_src_aliases  # noqa: E402
install_src_aliases(REPO_ROOT_HINT)

from tools.audit.arch_audit_common import (  # noqa: E402
    DEFAULT_AUDIT2_FINAL_DOC_REL,
    DEFAULT_AUDIT2_REPORT_JSON_REL,
    DEFAULT_AUDIT2_REPORT_MD_REL,
    DEFAULT_BASELINE_DOC_REL,
    DEFAULT_CONCURRENCY_SCAN_REPORT_MD_REL,
    DEFAULT_NUMERIC_SCAN_REPORT_MD_REL,
    DEFAULT_REPORT_JSON_REL,
    DEFAULT_REPORT_MD_REL,
    build_arch_audit2_report,
    build_concurrency_scan_report,
    build_numeric_scan_report,
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
    parser.add_argument("--numeric-scan-path", default=DEFAULT_NUMERIC_SCAN_REPORT_MD_REL)
    parser.add_argument("--concurrency-scan-path", default=DEFAULT_CONCURRENCY_SCAN_REPORT_MD_REL)
    parser.add_argument("--audit2-report-path", default=DEFAULT_AUDIT2_REPORT_MD_REL)
    parser.add_argument("--audit2-json-path", default=DEFAULT_AUDIT2_REPORT_JSON_REL)
    parser.add_argument("--audit2-final-path", default=DEFAULT_AUDIT2_FINAL_DOC_REL)
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
        numeric_scan_path=str(args.numeric_scan_path),
        concurrency_scan_path=str(args.concurrency_scan_path),
        audit2_report_path=str(args.audit2_report_path),
        audit2_json_path=str(args.audit2_json_path),
        audit2_final_path=str(args.audit2_final_path),
    )
    payload = dict(report)
    payload["numeric_scan_report"] = build_numeric_scan_report(report)
    payload["concurrency_scan_report"] = build_concurrency_scan_report(report)
    payload["audit2_report"] = build_arch_audit2_report(report)
    payload["written_outputs"] = written
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
