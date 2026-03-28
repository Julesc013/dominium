#!/usr/bin/env python3
"""Compare a previous release manifest against current build artifacts deterministically."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from release import DEFAULT_RELEASE_CHANNEL, build_release_manifest, load_release_manifest  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_json_text  # noqa: E402


def _token(value: object) -> str:
    return str(value or "").strip()


def _normalized_manifest(payload: dict) -> dict:
    out = dict(payload or {})
    out.pop("signatures", None)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify RELEASE-2 reproducibility against a previous manifest.")
    parser.add_argument("--previous-manifest", required=True)
    parser.add_argument("--dist-root", required=True)
    parser.add_argument("--platform-tag", required=True)
    parser.add_argument("--channel", default=DEFAULT_RELEASE_CHANNEL)
    parser.add_argument("--repo-root", default="")
    args = parser.parse_args(argv)

    previous_manifest_path = os.path.normpath(os.path.abspath(str(args.previous_manifest)))
    dist_root = os.path.normpath(os.path.abspath(str(args.dist_root)))
    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root))) if str(args.repo_root).strip() else ""

    try:
        previous = load_release_manifest(previous_manifest_path)
        current = build_release_manifest(
            dist_root,
            platform_tag=str(args.platform_tag).strip(),
            channel_id=str(args.channel).strip() or DEFAULT_RELEASE_CHANNEL,
            repo_root=repo_root,
            verify_build_ids=True,
        )
    except Exception as exc:
        payload = {
            "result": "refused",
            "match": False,
            "previous_manifest_path": previous_manifest_path.replace("\\", "/"),
            "dist_root": dist_root.replace("\\", "/"),
            "mismatches": [
                {
                    "field": "build_surface",
                    "code": "build_reproducibility_check_failed",
                    "message": str(exc),
                }
            ],
        }
        sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
        sys.stdout.write("\n")
        return 2

    mismatches: list[dict[str, str]] = []
    for field_name in ("release_id", "platform_tag", "semantic_contract_registry_hash", "manifest_hash", "deterministic_fingerprint"):
        if _token(previous.get(field_name)) != _token(current.get(field_name)):
            mismatches.append(
                {
                    "field": field_name,
                    "code": "manifest_field_mismatch",
                    "message": "field '{}' does not match".format(field_name),
                }
            )
    if canonical_json_text(list(previous.get("artifacts") or [])) != canonical_json_text(list(current.get("artifacts") or [])):
        mismatches.append(
            {
                "field": "artifacts",
                "code": "artifact_set_mismatch",
                "message": "artifact entries differ from the previous manifest",
            }
        )
    if canonical_json_text(_normalized_manifest(previous)) != canonical_json_text(_normalized_manifest(current)):
        mismatches.append(
            {
                "field": "manifest_body",
                "code": "manifest_body_mismatch",
                "message": "normalized release manifest body differs from the previous manifest",
            }
        )

    payload = {
        "result": "complete" if not mismatches else "refused",
        "match": not mismatches,
        "previous_manifest_path": previous_manifest_path.replace("\\", "/"),
        "dist_root": dist_root.replace("\\", "/"),
        "previous_manifest_hash": _token(previous.get("manifest_hash")).lower(),
        "current_manifest_hash": _token(current.get("manifest_hash")).lower(),
        "previous_release_id": _token(previous.get("release_id")),
        "current_release_id": _token(current.get("release_id")),
        "mismatches": mismatches,
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0 if not mismatches else 2


if __name__ == "__main__":
    raise SystemExit(main())
