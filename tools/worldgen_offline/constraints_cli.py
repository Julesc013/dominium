#!/usr/bin/env python3
"""Deterministic worldgen constraints command surface (set/clear/preview/commit)."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from worldgen.core.constraint_commands import (  # noqa: E402
    worldgen_constraints_clear,
    worldgen_constraints_set,
    worldgen_search_commit,
    worldgen_search_preview,
)


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def _authority_payload(args) -> dict:
    entitlements = sorted(
        set(str(item).strip() for item in list(getattr(args, "entitlement", []) or []) if str(item).strip())
    )
    return {
        "authority_origin": "tool",
        "privilege_level": str(getattr(args, "privilege_level", "operator")),
        "entitlements": entitlements,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Worldgen deterministic constraints command surface.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--privilege-level", default="operator", choices=("observer", "operator", "system"))
    parser.add_argument("--entitlement", action="append", default=[])
    sub = parser.add_subparsers(dest="command", required=True)

    set_cmd = sub.add_parser("worldgen.constraints.set")
    set_cmd.add_argument("--constraints-file", required=True)
    set_cmd.add_argument("--constraints-id", default="")
    set_cmd.add_argument("--base-seed", required=True)

    sub.add_parser("worldgen.constraints.clear")
    sub.add_parser("worldgen.search.preview")
    sub.add_parser("worldgen.search.commit")

    args = parser.parse_args()
    repo_root = _repo_root(str(args.repo_root))
    authority_context = _authority_payload(args)

    if args.command == "worldgen.constraints.set":
        result = worldgen_constraints_set(
            repo_root=repo_root,
            constraints_file=str(args.constraints_file),
            constraints_id=str(args.constraints_id),
            base_seed=str(args.base_seed),
            authority_context=authority_context,
        )
    elif args.command == "worldgen.constraints.clear":
        result = worldgen_constraints_clear(
            repo_root=repo_root,
            authority_context=authority_context,
        )
    elif args.command == "worldgen.search.preview":
        result = worldgen_search_preview(
            repo_root=repo_root,
            authority_context=authority_context,
        )
    elif args.command == "worldgen.search.commit":
        result = worldgen_search_commit(
            repo_root=repo_root,
            authority_context=authority_context,
        )
    else:
        parser.print_help()
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("result") == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())

