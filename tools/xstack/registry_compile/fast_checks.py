#!/usr/bin/env python3
"""FAST profile smoke checks for pack list + registry compile + lockfile validation + cache hit."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.pack_loader.pack_list import _pack_rows  # noqa: E402
from tools.xstack.pack_loader.loader import load_pack_set  # noqa: E402
from tools.xstack.pack_contrib.parser import parse_contributions  # noqa: E402
from tools.xstack.registry_compile.compiler import compile_bundle  # noqa: E402
from tools.xstack.registry_compile.constants import (  # noqa: E402
    DEFAULT_BUNDLE_ID,
    DEFAULT_LOCKFILE_OUT_REL,
    DEFAULT_REGISTRY_OUT_DIR_REL,
)
from tools.xstack.registry_compile.lockfile import validate_lockfile_payload  # noqa: E402


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def _load_json(path: str):
    try:
        return json.load(open(path, "r", encoding="utf-8")), ""
    except (OSError, ValueError):
        return None, "invalid json: {}".format(path.replace("\\", "/"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run FAST deterministic smoke checks for registry compile stack.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--bundle", default=DEFAULT_BUNDLE_ID)
    parser.add_argument("--out-dir", default=DEFAULT_REGISTRY_OUT_DIR_REL)
    parser.add_argument("--lockfile-out", default=DEFAULT_LOCKFILE_OUT_REL)
    parser.add_argument("--packs-root", default="packs")
    args = parser.parse_args()

    repo_root = _repo_root(args.repo_root)

    loaded = load_pack_set(repo_root=repo_root, packs_root_rel=str(args.packs_root))
    if loaded.get("result") != "complete":
        print(json.dumps(loaded, indent=2, sort_keys=True))
        return 2

    contrib = parse_contributions(repo_root=repo_root, packs=loaded.get("packs") or [])
    if contrib.get("result") != "complete":
        print(json.dumps(contrib, indent=2, sort_keys=True))
        return 2

    compile1 = compile_bundle(
        repo_root=repo_root,
        bundle_id=str(args.bundle),
        out_dir_rel=str(args.out_dir),
        lockfile_out_rel=str(args.lockfile_out),
        packs_root_rel=str(args.packs_root),
    )
    if compile1.get("result") != "complete":
        print(json.dumps(compile1, indent=2, sort_keys=True))
        return 2

    compile2 = compile_bundle(
        repo_root=repo_root,
        bundle_id=str(args.bundle),
        out_dir_rel=str(args.out_dir),
        lockfile_out_rel=str(args.lockfile_out),
        packs_root_rel=str(args.packs_root),
    )
    if compile2.get("result") != "complete":
        print(json.dumps(compile2, indent=2, sort_keys=True))
        return 2
    if not bool(compile2.get("cache_hit", False)):
        out = {
            "result": "refused",
            "errors": [
                {
                    "code": "refuse.registry_compile.fast_cache_miss",
                    "message": "second compile pass must be cache hit",
                    "path": "$.cache_hit",
                }
            ],
        }
        print(json.dumps(out, indent=2, sort_keys=True))
        return 2

    lockfile_path = os.path.join(repo_root, str(args.lockfile_out).replace("/", os.sep))
    lock_payload, lock_error = _load_json(lockfile_path)
    if lock_error:
        out = {
            "result": "refused",
            "errors": [
                {
                    "code": "refuse.lockfile.missing_or_invalid",
                    "message": lock_error,
                    "path": "$.lockfile",
                }
            ],
        }
        print(json.dumps(out, indent=2, sort_keys=True))
        return 2

    lock_validation = validate_lockfile_payload(lock_payload if isinstance(lock_payload, dict) else {})
    if lock_validation.get("result") != "complete":
        print(json.dumps(lock_validation, indent=2, sort_keys=True))
        return 2

    out = {
        "result": "complete",
        "bundle_id": str(args.bundle),
        "pack_count": int(loaded.get("pack_count", 0)),
        "contribution_count": int(contrib.get("contribution_count", 0)),
        "packs": _pack_rows(loaded.get("packs") or []),
        "cache_key": str(compile2.get("cache_key", "")),
        "cache_hit_second_run": True,
        "lockfile_path": str(args.lockfile_out).replace("\\", "/"),
        "pack_lock_hash": str((lock_payload or {}).get("pack_lock_hash", "")),
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

