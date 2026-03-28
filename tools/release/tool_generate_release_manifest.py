#!/usr/bin/env python3
"""Generate a deterministic RELEASE-1 manifest for a distribution directory."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from release import DEFAULT_RELEASE_CHANNEL, build_release_manifest, write_release_manifest  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a deterministic RELEASE-1 manifest for a distribution directory.")
    parser.add_argument("--dist-root", required=True)
    parser.add_argument("--platform-tag", required=True)
    parser.add_argument("--channel", default=DEFAULT_RELEASE_CHANNEL)
    parser.add_argument("--manifest-path", default="")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--check-build-id-consistency", action="store_true")
    args = parser.parse_args(argv)

    dist_root = os.path.normpath(os.path.abspath(str(args.dist_root)))
    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root))) if str(args.repo_root).strip() else ""
    manifest = build_release_manifest(
        dist_root,
        platform_tag=str(args.platform_tag).strip(),
        channel_id=str(args.channel).strip() or DEFAULT_RELEASE_CHANNEL,
        repo_root=repo_root,
        verify_build_ids=bool(args.check_build_id_consistency),
    )
    written_path = write_release_manifest(dist_root, manifest, manifest_path=str(args.manifest_path).strip())
    payload = {
        "result": "complete",
        "release_id": str(manifest.get("release_id", "")).strip(),
        "manifest_hash": str(manifest.get("manifest_hash", "")).strip(),
        "artifact_count": int(len(list(manifest.get("artifacts") or []))),
        "manifest_path": written_path,
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
