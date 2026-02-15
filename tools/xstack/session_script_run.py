#!/usr/bin/env python3
"""CLI: deterministic headless intent script runner (SRZ scheduling) for SessionSpec saves."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.sessionx.script_runner import run_intent_script  # noqa: E402


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay deterministic intent scripts through process runtime.")
    parser.add_argument("session_spec_path", help="path to saves/<save_id>/session_spec.json")
    parser.add_argument("script_path", help="path to JSON script file containing intents[]")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--bundle", default="")
    parser.add_argument("--compile-if-missing", default="off", choices=("on", "off"))
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--logical-shards", type=int, default=1)
    parser.add_argument("--write-state", default="on", choices=("on", "off"))
    parser.add_argument("--lockfile", default="")
    parser.add_argument("--registries-dir", default="")
    args = parser.parse_args()

    repo_root = _repo_root(args.repo_root)
    result = run_intent_script(
        repo_root=repo_root,
        session_spec_path=str(args.session_spec_path),
        script_path=str(args.script_path),
        bundle_id=str(args.bundle),
        compile_if_missing=str(args.compile_if_missing).strip().lower() == "on",
        workers=int(args.workers),
        write_state=str(args.write_state).strip().lower() != "off",
        logical_shards=int(args.logical_shards),
        lockfile_path=str(args.lockfile),
        registries_dir=str(args.registries_dir),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("result") == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
