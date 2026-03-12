#!/usr/bin/env python3
"""Build deterministic UI-RECONCILE-0 reports."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.release.ui_reconcile_common import (  # noqa: E402
    UI_RECONCILE_FINAL_PATH,
    UI_SURFACE_MAP_PATH,
    UI_SURFACE_REPORT_PATH,
    build_ui_reconcile_report,
    write_ui_reconcile_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    report = build_ui_reconcile_report(repo_root)
    write_ui_reconcile_outputs(repo_root, report)
    report = build_ui_reconcile_report(repo_root)
    written = write_ui_reconcile_outputs(repo_root, report)
    payload = {
        "result": str(report.get("result", "")).strip() or "unknown",
        "report_id": str(report.get("report_id", "")).strip(),
        "governed_surface_count": int(len(list(report.get("governed_surfaces") or []))),
        "legacy_surface_count": int(len(list(report.get("legacy_surfaces") or []))),
        "violation_count": int(len(list(report.get("violations") or []))),
        "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
        "surface_map_path": UI_SURFACE_MAP_PATH,
        "report_json_path": UI_SURFACE_REPORT_PATH,
        "final_doc_path": UI_RECONCILE_FINAL_PATH,
        "written_outputs": written,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["result"] == "complete" and payload["violation_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
