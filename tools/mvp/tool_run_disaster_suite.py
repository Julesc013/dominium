#!/usr/bin/env python3
"""Run the deterministic Omega disaster suite against the committed baseline cases."""

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

from tools.mvp.disaster_suite_common import (  # noqa: E402
    DISASTER_BASELINE_DOC_REL,
    DISASTER_BASELINE_REL,
    DISASTER_RUN_DOC_REL,
    DISASTER_RUN_JSON_REL,
    run_disaster_suite,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--cases-path", default="")
    parser.add_argument("--output-root-rel", default="")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    report = run_disaster_suite(
        repo_root,
        cases_path=str(args.cases_path or ""),
        output_root_rel=str(args.output_root_rel or ""),
        write_outputs=True,
    )
    written = dict(report.get("written") or {})
    payload = {
        "result": str(report.get("result", "")).strip(),
        "case_count": int(report.get("case_count", 0) or 0),
        "matched_case_count": int(report.get("matched_case_count", 0) or 0),
        "mismatched_case_count": int(report.get("mismatched_case_count", 0) or 0),
        "run_json_rel": os.path.relpath(str(written.get("run_json_path", "")), repo_root).replace("\\", "/") if str(written.get("run_json_path", "")).strip() else DISASTER_RUN_JSON_REL,
        "run_doc_rel": os.path.relpath(str(written.get("run_doc_path", "")), repo_root).replace("\\", "/") if str(written.get("run_doc_path", "")).strip() else DISASTER_RUN_DOC_REL,
        "baseline_rel": os.path.relpath(str(written.get("baseline_path", "")), repo_root).replace("\\", "/") if str(written.get("baseline_path", "")).strip() else DISASTER_BASELINE_REL,
        "baseline_doc_rel": os.path.relpath(str(written.get("baseline_doc_path", "")), repo_root).replace("\\", "/") if str(written.get("baseline_doc_path", "")).strip() else DISASTER_BASELINE_DOC_REL,
        "mismatched_fields": list(report.get("mismatched_fields") or []),
        "silent_success_case_ids": list(report.get("silent_success_case_ids") or []),
        "remediation_missing_case_ids": list(report.get("remediation_missing_case_ids") or []),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
