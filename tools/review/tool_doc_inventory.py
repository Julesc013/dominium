#!/usr/bin/env python3
"""Build the deterministic documentation inventory and canon reconciliation reports."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.doc_inventory_common import (  # noqa: E402
    DOC_INVENTORY_JSON_REL,
    REPO_REVIEW_3_FINAL_MD_REL,
    build_doc_inventory,
    load_or_run_doc_inventory,
    missing_stability_header_entries,
    superseded_without_replacement_entries,
    write_doc_inventory_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--prefer-cached", action="store_true")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    report = load_or_run_doc_inventory(repo_root, prefer_cached=bool(args.prefer_cached))
    if not report:
        report = build_doc_inventory(repo_root)
    written = write_doc_inventory_outputs(repo_root, report)
    payload = {
        "result": str(report.get("result", "")).strip() or "unknown",
        "inventory_path": DOC_INVENTORY_JSON_REL,
        "final_report_path": REPO_REVIEW_3_FINAL_MD_REL,
        "entry_count": int(report.get("entry_count", 0) or 0),
        "missing_stability_header_count": len(missing_stability_header_entries(report)),
        "missing_replacement_count": len(superseded_without_replacement_entries(report)),
        "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
        "written_outputs": written,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["result"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
