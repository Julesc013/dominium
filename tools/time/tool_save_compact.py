#!/usr/bin/env python3
"""Deterministic save compaction tool (RS-3)."""

from __future__ import annotations

import argparse
import json
import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.sessionx.time_lineage import compact_save


def _repo_root(value: str) -> str:
    token = str(value or "").strip()
    if token:
        return os.path.normpath(os.path.abspath(token))
    return REPO_ROOT_HINT


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic save compaction policy on a save lineage.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--save-id", required=True)
    parser.add_argument("--compaction-policy-id", required=True)
    args = parser.parse_args()

    result = compact_save(
        repo_root=_repo_root(args.repo_root),
        save_id=str(args.save_id),
        compaction_policy_id=str(args.compaction_policy_id),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
