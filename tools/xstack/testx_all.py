#!/usr/bin/env python3
"""Convenience TestX entrypoint with optional deterministic subset selection."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.testx import run_testx_suite  # noqa: E402


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def main() -> int:
    parser = argparse.ArgumentParser(description="Run TestX all-suite with optional deterministic subset selection.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--profile", default="STRICT", choices=("FAST", "STRICT", "FULL"))
    parser.add_argument("--cache", default="on", choices=("on", "off"))
    parser.add_argument("--shards", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--subset", action="append", default=[], help="comma-separated test IDs")
    args = parser.parse_args()

    result = run_testx_suite(
        repo_root=_repo_root(args.repo_root),
        profile=str(args.profile),
        shards=int(args.shards),
        shard_index=int(args.shard_index),
        cache_enabled=str(args.cache).strip().lower() != "off",
        subset=list(args.subset or []),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    status = str(result.get("status", "error"))
    if status == "pass":
        return 0
    if status == "refusal":
        return 2
    if status == "fail":
        return 1
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
