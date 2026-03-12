#!/usr/bin/env python3
"""Build deterministic APPSHELL-PLATFORM-1 UI mode resolution reports."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.release.ui_mode_resolution_common import (  # noqa: E402
    UI_MODE_RESOLUTION_BASELINE_PATH,
    UI_MODE_RESOLUTION_DOC_PATH,
    build_ui_mode_resolution_report,
    write_ui_mode_resolution_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    report = build_ui_mode_resolution_report(repo_root)
    written = write_ui_mode_resolution_outputs(repo_root, report)
    payload = {
        "result": str(report.get("result", "")).strip() or "unknown",
        "report_id": str(report.get("report_id", "")).strip(),
        "policy_count": int(len(list(report.get("policy_rows") or []))),
        "selection_count": int(len(list(report.get("selection_rows") or []))),
        "violation_count": int(len(list(report.get("violations") or []))),
        "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
        "doc_path": UI_MODE_RESOLUTION_DOC_PATH,
        "baseline_path": UI_MODE_RESOLUTION_BASELINE_PATH,
        "written_outputs": written,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["result"] == "complete" and payload["violation_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
