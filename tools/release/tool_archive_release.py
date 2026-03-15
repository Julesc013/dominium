#!/usr/bin/env python3
"""Create deterministic ARCHIVE-POLICY-0 records for a release bundle."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.release.archive_policy_common import DEFAULT_PLATFORM_TAG, archive_release


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic archive records for a release bundle.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--dist-root", default="")
    parser.add_argument("--platform-tag", default=DEFAULT_PLATFORM_TAG)
    parser.add_argument("--release-id", default="")
    parser.add_argument("--source-archive", default="")
    parser.add_argument("--archive-record-path", default="")
    parser.add_argument("--write-offline-bundle", action="store_true")
    parser.add_argument("--mirror", action="append", default=[])
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    dist_root = str(args.dist_root or "").strip()
    if not dist_root:
        dist_root = os.path.join(repo_root, "dist", "v0.0.0-mock", str(args.platform_tag or DEFAULT_PLATFORM_TAG).strip() or DEFAULT_PLATFORM_TAG, "dominium")
    result = archive_release(
        repo_root,
        dist_root=dist_root,
        release_id=str(args.release_id or "").strip(),
        mirror_list=list(args.mirror or []),
        source_archive_path=str(args.source_archive or "").strip(),
        archive_record_path=str(args.archive_record_path or "").strip(),
        write_offline_bundle=bool(args.write_offline_bundle),
    )
    print(
        json.dumps(
            {
                "result": str(result.get("result", "")).strip(),
                "release_id": str(result.get("release_id", "")).strip(),
                "archive_record_hash": str(result.get("archive_record_hash", "")).strip(),
                "archive_record_path": str(result.get("archive_record_path", "")).strip(),
                "release_index_history_rel": str(result.get("release_index_history_rel", "")).strip(),
                "offline_bundle_hash": str(dict(result.get("offline_bundle") or {}).get("bundle_hash", "")).strip(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
