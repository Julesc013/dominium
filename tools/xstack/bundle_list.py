#!/usr/bin/env python3
"""CLI: list deterministic bundle profiles from bundles/<bundle_id>/bundle.json."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.registry_compile.bundle_profile import load_bundle_profiles  # noqa: E402


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def main() -> int:
    parser = argparse.ArgumentParser(description="List bundle profiles in deterministic order.")
    parser.add_argument("--repo-root", default="")
    args = parser.parse_args()

    repo_root = _repo_root(args.repo_root)
    result = load_bundle_profiles(repo_root=repo_root)
    if result.get("result") != "complete":
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2

    rows = []
    for row in sorted(result.get("bundles") or [], key=lambda item: str(item.get("bundle_id", ""))):
        rows.append(
            {
                "bundle_id": str(row.get("bundle_id", "")),
                "description": str(row.get("description", "")),
                "pack_count": len(row.get("pack_ids") or []),
                "optional_pack_count": len(row.get("optional_pack_ids") or []),
                "bundle_path": str(row.get("bundle_path", "")),
            }
        )

    payload = {
        "result": "complete",
        "bundle_count": len(rows),
        "bundles": rows,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
