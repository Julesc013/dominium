#!/usr/bin/env python3
"""Run the deterministic DIST-6 version interop matrix."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.dist.dist6_interop_common import (
    DIST6_CASE_IDS,
    build_version_interop_reports,
    write_version_interop_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic DIST-6 version interop checks.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--dist-root-a", default="")
    parser.add_argument("--dist-root-b", default="")
    parser.add_argument("--platform-tag-a", default="win64")
    parser.add_argument("--platform-tag-b", default="win64")
    parser.add_argument("--channel", default="mock")
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--work-root", default="")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    case_ids = [str(item).strip() for item in list(args.case_id or []) if str(item).strip()]
    unknown_case_ids = sorted(set(case_ids) - set(DIST6_CASE_IDS))
    if unknown_case_ids:
        parser.error("unknown --case-id values: {}".format(", ".join(unknown_case_ids)))

    reports = build_version_interop_reports(
        repo_root,
        dist_root_a=str(args.dist_root_a or "").strip(),
        dist_root_b=str(args.dist_root_b or "").strip(),
        platform_tag_a=str(args.platform_tag_a or "win64").strip() or "win64",
        platform_tag_b=str(args.platform_tag_b or "win64").strip() or "win64",
        channel_id=str(args.channel or "mock").strip() or "mock",
        case_ids=case_ids or None,
        work_root=str(args.work_root or "").strip(),
    )
    outputs = write_version_interop_outputs(repo_root, reports)
    final_report = dict(outputs.get("final_report") or {})
    payload = {
        "result": str(final_report.get("result", "")).strip(),
        "case_ids": list(final_report.get("case_ids") or []),
        "failure_count": int(final_report.get("failure_count", 0) or 0),
        "deterministic_fingerprint": str(final_report.get("deterministic_fingerprint", "")).strip(),
        "final_doc_path": str(outputs.get("final_doc_path", "")).strip(),
        "case_outputs": list(outputs.get("case_outputs") or []),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["result"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
