#!/usr/bin/env python3
"""Deterministic setup build command for dist layout packaging."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.packagingx import build_dist_layout, validate_dist_layout  # noqa: E402
from tools.xstack.registry_compile.constants import DEFAULT_BUNDLE_ID  # noqa: E402


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def _as_text(payload: dict) -> str:
    if payload.get("result") != "complete":
        first = (payload.get("errors") or [{}])[0]
        return "[setup.build] result=refused code={} message={}".format(
            str(first.get("code", "")),
            str(first.get("message", "")),
        )
    return "[setup.build] result=complete bundle={} out={} content_hash={}".format(
        str(payload.get("bundle_id", "")),
        str(payload.get("out_dir", "")),
        str(payload.get("canonical_content_hash", "")),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic dist layout for a bundle.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--bundle", default=DEFAULT_BUNDLE_ID)
    parser.add_argument("--out", default="dist")
    parser.add_argument("--cache", default="on", choices=("on", "off"))
    parser.add_argument("--format", default="json", choices=("json", "text"))
    args = parser.parse_args()

    repo_root = _repo_root(args.repo_root)
    built = build_dist_layout(
        repo_root=repo_root,
        bundle_id=str(args.bundle),
        out_dir=str(args.out),
        use_cache=str(args.cache).strip().lower() != "off",
    )
    if built.get("result") == "complete":
        verified = validate_dist_layout(repo_root=repo_root, dist_root=str(args.out))
        if verified.get("result") != "complete":
            built = verified
        else:
            built["validation"] = verified
    if str(args.format) == "text":
        print(_as_text(built))
    else:
        print(json.dumps(built, indent=2, sort_keys=True))
    return 0 if built.get("result") == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())

