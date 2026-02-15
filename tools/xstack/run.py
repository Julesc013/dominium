#!/usr/bin/env python3
"""Stable XStack entrypoint for FAST/STRICT/FULL deterministic profile runs."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.controlx import run_profile  # noqa: E402
from tools.xstack.controlx.types import RunContext  # noqa: E402


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def _profile_token(raw: str) -> str:
    token = str(raw or "").strip().upper()
    if token == "VERIFY":
        return "FAST"
    if token in ("FAST", "STRICT", "FULL"):
        return token
    return ""


def _output_dir(repo_root: str, profile: str) -> str:
    return os.path.join(
        repo_root,
        "tools",
        "xstack",
        "out",
        str(profile).strip().lower(),
        "latest",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic XStack profile checks.")
    sub = parser.add_subparsers(dest="command")

    for name in ("fast", "strict", "full"):
        item = sub.add_parser(name, help="run {} profile".format(name.upper()))
        item.add_argument("--repo-root", default="")
        item.add_argument("--cache", default="on", choices=("on", "off"))
        if name == "full":
            item.add_argument("--shards", type=int, default=1)
            item.add_argument("--shard-index", type=int, default=0)

    parser.add_argument("--repo-root", default="")
    parser.add_argument("--cache", default="on", choices=("on", "off"))
    parser.add_argument("--shards", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--skip-testx", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("legacy_profile", nargs="?")
    return parser


def _resolve_args(args: argparse.Namespace):
    command = str(getattr(args, "command", "") or "").strip()
    legacy = str(getattr(args, "legacy_profile", "") or "").strip()
    profile = _profile_token(command) or _profile_token(legacy)
    if not profile:
        return "", 1, 0, True, _repo_root(str(getattr(args, "repo_root", "") or ""))

    shards = int(getattr(args, "shards", 1) or 1)
    shard_index = int(getattr(args, "shard_index", 0) or 0)
    if profile in ("FAST", "STRICT"):
        shards = 1
        shard_index = 0
    cache_enabled = str(getattr(args, "cache", "on")).strip().lower() != "off"
    return profile, shards, shard_index, cache_enabled, _repo_root(str(getattr(args, "repo_root", "") or ""))


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    profile, shards, shard_index, cache_enabled, repo_root = _resolve_args(args)
    if not profile:
        parser.print_help()
        return 2

    skip_testx = bool(args.skip_testx or str(os.environ.get("DOM_XSTACK_SKIP_TESTX", "")).strip() == "1")
    context = RunContext(
        repo_root=repo_root,
        profile=profile,
        cache_enabled=cache_enabled,
        shards=shards,
        shard_index=shard_index,
        output_dir=_output_dir(repo_root, profile),
        skip_testx=skip_testx,
    )
    report = run_profile(context)
    for line in report.get("summary_lines") or []:
        print(line)
    print(json.dumps(report, indent=2, sort_keys=True))
    return int(report.get("exit_code", 3))


if __name__ == "__main__":
    raise SystemExit(main())
