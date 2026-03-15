#!/usr/bin/env python3
"""Run deterministic GOVERNANCE-0 reporting."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.governance.governance_model_common import write_governance_outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic GOVERNANCE-0 reporting.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--platform-tag", default="win64")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    outputs = write_governance_outputs(repo_root, platform_tag=str(args.platform_tag or "win64").strip() or "win64")
    report = dict(outputs.get("report") or {})
    sys.stdout.write(
        json.dumps(
            {
                "result": str(report.get("result", "")).strip(),
                "governance_mode_id": str(report.get("governance_mode_id", "")).strip(),
                "governance_profile_hash": str(report.get("governance_profile_hash", "")).strip(),
                "release_index_governance_hash": str(report.get("release_index_governance_hash", "")).strip(),
                "violation_count": int(len(list(report.get("violations") or []))),
                "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
                "baseline_doc_path": str(outputs.get("baseline_doc_path", "")).strip(),
                "report_json_path": str(outputs.get("report_json_path", "")).strip(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    sys.stdout.write("\n")
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
