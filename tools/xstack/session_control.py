#!/usr/bin/env python3
"""CLI: deterministic session pipeline stage/abort/resume controls."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.sessionx.session_control import (  # noqa: E402
    abort_session_spec,
    compact_session_save,
    resume_session_spec,
    session_stage_status,
)


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def _add_stage_command(subparsers) -> None:
    parser = subparsers.add_parser(
        "client.session.stage",
        help="print deterministic session stage + stage log",
    )
    parser.add_argument("session_spec_path", help="path to saves/<save_id>/session_spec.json")
    parser.add_argument("--repo-root", default="")


def _add_abort_command(subparsers) -> None:
    parser = subparsers.add_parser(
        "client.session.abort",
        help="write deterministic abort snapshot for a session",
    )
    parser.add_argument("session_spec_path", help="path to saves/<save_id>/session_spec.json")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--stage-id", default="", help="optional explicit stage id to abort from")
    parser.add_argument("--reason", default="manual_abort")


def _add_resume_command(subparsers) -> None:
    parser = subparsers.add_parser(
        "client.session.resume",
        help="resume a deterministic session snapshot through canonical re-entry checks",
    )
    parser.add_argument("session_spec_path", help="path to saves/<save_id>/session_spec.json")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--bundle", default="")
    parser.add_argument("--lockfile", default="")
    parser.add_argument("--registries-dir", default="")


def _add_compact_command(subparsers) -> None:
    parser = subparsers.add_parser(
        "client.session.compact",
        help="run deterministic save compaction policy for the session save",
    )
    parser.add_argument("session_spec_path", help="path to saves/<save_id>/session_spec.json")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--compaction-policy-id", required=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Session pipeline controls (stage/abort/resume).")
    sub = parser.add_subparsers(dest="command")
    _add_stage_command(sub)
    _add_abort_command(sub)
    _add_resume_command(sub)
    _add_compact_command(sub)
    args = parser.parse_args()
    command = str(getattr(args, "command", "") or "").strip()
    repo_root = _repo_root(str(getattr(args, "repo_root", "") or ""))

    if command == "client.session.stage":
        result = session_stage_status(
            repo_root=repo_root,
            session_spec_path=str(args.session_spec_path),
        )
    elif command == "client.session.abort":
        result = abort_session_spec(
            repo_root=repo_root,
            session_spec_path=str(args.session_spec_path),
            stage_id=str(args.stage_id),
            reason=str(args.reason),
        )
    elif command == "client.session.resume":
        result = resume_session_spec(
            repo_root=repo_root,
            session_spec_path=str(args.session_spec_path),
            bundle_id=str(args.bundle),
            lockfile_path=str(args.lockfile),
            registries_dir=str(args.registries_dir),
        )
    elif command == "client.session.compact":
        result = compact_session_save(
            repo_root=repo_root,
            session_spec_path=str(args.session_spec_path),
            compaction_policy_id=str(args.compaction_policy_id),
        )
    else:
        parser.print_help()
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("result") == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
