#!/usr/bin/env python3
"""Build the deterministic Omega offline archive bundle for v0.0.0-mock."""

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

from tools.release.offline_archive_common import (  # noqa: E402
    DEFAULT_DIST_ROOT_REL,
    DEFAULT_PLATFORM_TAG,
    DEFAULT_RELEASE_ID,
    build_offline_archive,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--release-id", default=DEFAULT_RELEASE_ID)
    parser.add_argument("--dist-root", default=DEFAULT_DIST_ROOT_REL)
    parser.add_argument("--artifact-store-path", default="")
    parser.add_argument("--platform-tag", default=DEFAULT_PLATFORM_TAG)
    parser.add_argument("--output-root-rel", default="")
    parser.add_argument("--include-source-snapshot", action="store_true")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    report = build_offline_archive(
        repo_root,
        release_id=str(args.release_id or DEFAULT_RELEASE_ID).strip() or DEFAULT_RELEASE_ID,
        dist_root=str(args.dist_root or DEFAULT_DIST_ROOT_REL).strip() or DEFAULT_DIST_ROOT_REL,
        artifact_store_path=str(args.artifact_store_path or "").strip(),
        platform_tag=str(args.platform_tag or DEFAULT_PLATFORM_TAG).strip() or DEFAULT_PLATFORM_TAG,
        output_root_rel=str(args.output_root_rel or "").strip(),
        include_source_snapshot=bool(args.include_source_snapshot),
    )
    print(
        json.dumps(
            {
                "result": str(report.get("result", "")).strip(),
                "release_id": str(report.get("release_id", "")).strip(),
                "archive_bundle_rel": str(report.get("archive_bundle_rel", "")).strip(),
                "archive_bundle_hash": str(report.get("archive_bundle_hash", "")).strip(),
                "archive_record_hash": str(report.get("archive_record_hash", "")).strip(),
                "archive_projection_hash": str(report.get("archive_projection_hash", "")).strip(),
                "artifact_count": int(report.get("artifact_count", 0) or 0),
                "support_surface_count": int(report.get("support_surface_count", 0) or 0),
                "member_count": int(report.get("member_count", 0) or 0),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
