#!/usr/bin/env python3
"""Run deterministic ARCHIVE-POLICY-0 generation and baseline reporting."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.release.archive_policy_common import DEFAULT_PLATFORM_TAG, write_archive_policy_outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic ARCHIVE-POLICY-0 generation.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--platform-tag", default=DEFAULT_PLATFORM_TAG)
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    outputs = write_archive_policy_outputs(repo_root, platform_tag=str(args.platform_tag or DEFAULT_PLATFORM_TAG).strip() or DEFAULT_PLATFORM_TAG)
    report = dict(outputs.get("report") or {})
    print(
        json.dumps(
            {
                "result": str(report.get("result", "")).strip(),
                "archive_record_hash": str(report.get("archive_record_hash", "")).strip(),
                "release_index_hash": str(report.get("release_index_hash", "")).strip(),
                "offline_bundle_hash": str(report.get("offline_bundle_hash", "")).strip(),
                "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
                "baseline_doc_path": str(outputs.get("baseline_doc_path", "")).strip(),
                "report_json_path": str(outputs.get("report_json_path", "")).strip(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
