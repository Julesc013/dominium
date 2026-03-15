#!/usr/bin/env python3
"""Verify deterministic ARCHIVE-POLICY-0 release retention artifacts."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.release.archive_policy_common import DEFAULT_PLATFORM_TAG, verify_archive


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify deterministic archive records and index history.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--dist-root", default="")
    parser.add_argument("--platform-tag", default=DEFAULT_PLATFORM_TAG)
    parser.add_argument("--archive-record-path", default="")
    parser.add_argument("--source-archive", default="")
    parser.add_argument("--check-mirrors", action="store_true")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    dist_root = str(args.dist_root or "").strip()
    if not dist_root:
        dist_root = os.path.join(repo_root, "dist", "v0.0.0-mock", str(args.platform_tag or DEFAULT_PLATFORM_TAG).strip() or DEFAULT_PLATFORM_TAG, "dominium")
    result = verify_archive(
        repo_root,
        dist_root=dist_root,
        archive_record_path=str(args.archive_record_path or "").strip(),
        source_archive_path=str(args.source_archive or "").strip(),
        check_mirrors=bool(args.check_mirrors),
    )
    print(
        json.dumps(
            {
                "result": str(result.get("result", "")).strip(),
                "archive_record_hash": str(result.get("archive_record_hash", "")).strip(),
                "release_index_hash": str(result.get("release_index_hash", "")).strip(),
                "error_count": int(len(list(result.get("errors") or []))),
                "warning_count": int(len(list(result.get("warnings") or []))),
                "deterministic_fingerprint": str(result.get("deterministic_fingerprint", "")).strip(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if str(result.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
