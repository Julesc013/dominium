#!/usr/bin/env python3
"""CLI: deterministic server-side session pipeline enforcement checks."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.sessionx.server_gate import server_validate_transition  # noqa: E402


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def _load_authority(path: str) -> dict:
    if not str(path).strip():
        return {}
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate server-side stage + authority constraints for SessionSpec transitions.")
    parser.add_argument("session_spec_path", help="path to saves/<save_id>/session_spec.json")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--from-stage", default="")
    parser.add_argument("--to-stage", default="stage.session_running")
    parser.add_argument("--authority-context", default="", help="optional authority context JSON file")
    args = parser.parse_args()

    repo_root = _repo_root(str(args.repo_root))
    result = server_validate_transition(
        repo_root=repo_root,
        session_spec_path=str(args.session_spec_path),
        from_stage_id=str(args.from_stage),
        to_stage_id=str(args.to_stage),
        authority_context=_load_authority(str(args.authority_context)),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("result") == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
