#!/usr/bin/env python3
"""Run the deterministic Ω-10 DIST final dry-run readiness check."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.release.dist_final_common import (  # noqa: E402
    DIST_FINAL_DRYRUN_DOC_REL,
    build_dist_final_dryrun_report,
    write_dist_final_dryrun_doc,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--doc-path", default=DIST_FINAL_DRYRUN_DOC_REL)
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    report = build_dist_final_dryrun_report(repo_root)
    doc_path = write_dist_final_dryrun_doc(repo_root, report, doc_path=str(args.doc_path or DIST_FINAL_DRYRUN_DOC_REL).strip())
    payload = {
        "artifact_issue_count": int(report.get("artifact_issue_count", 0) or 0),
        "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
        "doc_path": os.path.relpath(doc_path, repo_root).replace("\\", "/"),
        "missing_count": int(report.get("missing_count", 0) or 0),
        "result": str(report.get("result", "")).strip(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["result"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
