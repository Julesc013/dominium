#!/usr/bin/env python3
"""CLI: deterministic pack discovery + listing for Pack System v1."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.pack_contrib.parser import parse_contributions  # noqa: E402
from tools.xstack.pack_loader.loader import load_pack_set  # noqa: E402


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def _pack_rows(packs: list) -> list:
    rows = []
    for row in sorted(packs, key=lambda item: str(item.get("pack_id", ""))):
        rows.append(
            {
                "pack_id": str(row.get("pack_id", "")),
                "category": str(row.get("category", "")),
                "version": str(row.get("version", "")),
                "dependency_count": len(row.get("dependencies") or []),
                "signature_status": str(row.get("signature_status", "")),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="List canonical packs in deterministic order.")
    parser.add_argument("--repo-root", default="")
    args = parser.parse_args()

    repo_root = _repo_root(args.repo_root)
    loaded = load_pack_set(repo_root=repo_root)
    if loaded.get("result") == "refused":
        print(json.dumps(loaded, indent=2, sort_keys=True))
        return 2

    contrib = parse_contributions(repo_root=repo_root, packs=loaded.get("packs") or [])
    if contrib.get("result") == "refused":
        print(json.dumps(contrib, indent=2, sort_keys=True))
        return 2

    payload = {
        "result": "complete",
        "pack_count": int(loaded.get("pack_count", 0)),
        "contribution_count": int(contrib.get("contribution_count", 0)),
        "packs": _pack_rows(loaded.get("packs") or []),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

