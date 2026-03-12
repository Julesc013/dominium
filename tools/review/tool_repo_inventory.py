#!/usr/bin/env python3
"""Build the deterministic repository inventory and derived review reports."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.repo_inventory_common import (  # noqa: E402
    FINAL_REPORT_REL,
    INVENTORY_JSON_REL,
    build_repo_inventory,
    load_or_run_inventory_report,
    unknown_inventory_entries,
    write_repo_inventory_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--prefer-cached", action="store_true")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    report = load_or_run_inventory_report(repo_root, prefer_cached=bool(args.prefer_cached))
    if not report:
        report = build_repo_inventory(repo_root)
    written = write_repo_inventory_outputs(repo_root, report)
    payload = {
        "result": str(report.get("result", "")).strip() or "unknown",
        "inventory_path": INVENTORY_JSON_REL,
        "final_report_path": FINAL_REPORT_REL,
        "entry_count": int(report.get("entry_count", 0) or 0),
        "unknown_entry_count": len(unknown_inventory_entries(report)),
        "bypass_count": len(list(dict(report.get("entrypoint_map") or {}).get("bypasses") or [])),
        "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
        "written_outputs": written,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["result"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
