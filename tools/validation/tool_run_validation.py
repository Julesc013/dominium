#!/usr/bin/env python3
"""Run the unified validation pipeline and write deterministic reports."""

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


from validation import (  # noqa: E402
    VALIDATION_FINAL_DOC_TEMPLATE,
    VALIDATION_INVENTORY_DOC_PATH,
    VALIDATION_REPORT_DOC_TEMPLATE,
    VALIDATION_REPORT_JSON_TEMPLATE,
    build_validation_report,
    write_validation_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--profile", default="FAST", choices=("FAST", "STRICT", "FULL"))
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    profile = str(args.profile or "FAST").strip().upper() or "FAST"
    report = build_validation_report(repo_root, profile=profile)
    written = write_validation_outputs(repo_root, report)
    payload = {
        "result": str(report.get("result", "")).strip(),
        "profile": profile,
        "suite_count": int(dict(report.get("metrics") or {}).get("suite_count", 0) or 0),
        "error_count": len(list(report.get("errors") or [])),
        "warning_count": len(list(report.get("warnings") or [])),
        "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
        "inventory_path": VALIDATION_INVENTORY_DOC_PATH,
        "report_doc_path": VALIDATION_REPORT_DOC_TEMPLATE.format(profile=profile),
        "report_json_path": VALIDATION_REPORT_JSON_TEMPLATE.format(profile=profile),
        "final_doc_path": VALIDATION_FINAL_DOC_TEMPLATE,
        "written_outputs": written,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["result"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
