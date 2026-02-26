#!/usr/bin/env python3
"""Create deterministic branch lineage from a saved checkpoint artifact."""

from __future__ import annotations

import argparse
import json
import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.sessionx.time_lineage import branch_from_checkpoint


def _repo_root(value: str) -> str:
    if str(value or "").strip():
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def main() -> int:
    parser = argparse.ArgumentParser(description="Create deterministic branch lineage from checkpoint.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--parent-checkpoint-id", required=True)
    parser.add_argument("--new-save-id", required=True)
    parser.add_argument("--reason", default="user.tool.branch")
    parser.add_argument("--parent-save-id", default="")
    args = parser.parse_args()

    result = branch_from_checkpoint(
        repo_root=_repo_root(args.repo_root),
        parent_checkpoint_id=str(args.parent_checkpoint_id),
        new_save_id=str(args.new_save_id),
        reason=str(args.reason),
        parent_save_id=str(args.parent_save_id),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if str(result.get("result", "")) == "complete":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
