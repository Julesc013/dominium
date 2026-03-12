#!/usr/bin/env python3
"""Build deterministic ENTRYPOINT-UNIFY-0 reports."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.release.entrypoint_unify_common import (  # noqa: E402
    ENTRYPOINT_UNIFY_FINAL_PATH,
    ENTRYPOINT_UNIFY_MAP_PATH,
    FLAG_MIGRATION_PATH,
    build_entrypoint_unify_report,
    write_entrypoint_unify_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    report = build_entrypoint_unify_report(repo_root)
    written = write_entrypoint_unify_outputs(repo_root, report)
    payload = {
        "result": str(report.get("result", "")).strip() or "unknown",
        "report_id": str(report.get("inventory_id", "")).strip(),
        "entry_count": len(list(report.get("rows") or [])),
        "violation_count": len(list(report.get("violations") or [])),
        "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
        "map_path": ENTRYPOINT_UNIFY_MAP_PATH,
        "flag_migration_path": FLAG_MIGRATION_PATH,
        "final_report_path": ENTRYPOINT_UNIFY_FINAL_PATH,
        "written_outputs": written,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["result"] == "complete" and payload["violation_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
