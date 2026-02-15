#!/usr/bin/env python3
"""CLI: validate a bundle profile file against schemas/bundle_profile.schema.json."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from tools.xstack.registry_compile.bundle_profile import validate_bundle_file  # noqa: E402


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a bundle profile manifest file.")
    parser.add_argument("bundle_json", help="path to bundles/<bundle_id>/bundle.json")
    parser.add_argument("--repo-root", default="")
    args = parser.parse_args()

    repo_root = _repo_root(args.repo_root)
    result = validate_bundle_file(repo_root=repo_root, bundle_file_path=str(args.bundle_json))
    if result.get("result") != "complete":
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2

    payload = dict(result.get("payload") or {})
    out = {
        "result": "complete",
        "bundle_id": str(result.get("bundle_id", "")),
        "bundle_path": str(result.get("bundle_path", "")),
        "pack_ids": list(result.get("pack_ids") or []),
        "optional_pack_ids": list(result.get("optional_pack_ids") or []),
        "payload_hash": canonical_sha256(payload),
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
