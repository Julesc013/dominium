#!/usr/bin/env python3
"""CLI: build deterministic bundle lockfile (and compile registries)."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.registry_compile.compiler import compile_bundle  # noqa: E402
from tools.xstack.registry_compile.constants import (  # noqa: E402
    DEFAULT_BUNDLE_ID,
    DEFAULT_LOCKFILE_OUT_REL,
    DEFAULT_REGISTRY_OUT_DIR_REL,
)


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic lockfile and derived registries.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--bundle", default=DEFAULT_BUNDLE_ID)
    parser.add_argument("--out", default=DEFAULT_LOCKFILE_OUT_REL)
    parser.add_argument("--registry-out-dir", default=DEFAULT_REGISTRY_OUT_DIR_REL)
    parser.add_argument("--packs-root", default="packs")
    args = parser.parse_args()

    repo_root = _repo_root(args.repo_root)
    result = compile_bundle(
        repo_root=repo_root,
        bundle_id=str(args.bundle),
        out_dir_rel=str(args.registry_out_dir),
        lockfile_out_rel=str(args.out),
        packs_root_rel=str(args.packs_root),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("result") == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())

