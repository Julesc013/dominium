#!/usr/bin/env python3
"""Generate deterministic platform formalization reports."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.release.platform_formalize_common import build_platform_formalize_report, write_platform_formalize_outputs  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate PLATFORM-FORMALIZE-0 deterministic audit outputs.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root)))
    report = build_platform_formalize_report(repo_root)
    written = write_platform_formalize_outputs(repo_root, report)
    payload = {
        "result": str(report.get("result", "")).strip() or "complete",
        "report_id": str(report.get("report_id", "")).strip(),
        "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
        "violation_count": int(len(list(report.get("violations") or []))),
        "written_outputs": dict(written),
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0 if str(report.get("result", "")).strip() == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
