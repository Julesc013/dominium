#!/usr/bin/env python3
"""CLI: parity adapter for CLI/TUI/GUI session stage controls."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.sessionx.stage_parity import (  # noqa: E402
    surface_abort_session,
    surface_compact_session,
    surface_resume_session,
    surface_stage_status,
)


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def main() -> int:
    parser = argparse.ArgumentParser(description="Session stage parity controls for cli|tui|gui.")
    parser.add_argument("--surface", default="cli", choices=("cli", "tui", "gui"))
    parser.add_argument("--repo-root", default="")
    sub = parser.add_subparsers(dest="command")

    stage_cmd = sub.add_parser("client.session.stage")
    stage_cmd.add_argument("session_spec_path")

    abort_cmd = sub.add_parser("client.session.abort")
    abort_cmd.add_argument("session_spec_path")
    abort_cmd.add_argument("--stage-id", default="")
    abort_cmd.add_argument("--reason", default="manual_abort")

    resume_cmd = sub.add_parser("client.session.resume")
    resume_cmd.add_argument("session_spec_path")
    resume_cmd.add_argument("--bundle", default="")
    resume_cmd.add_argument("--lockfile", default="")
    resume_cmd.add_argument("--registries-dir", default="")

    compact_cmd = sub.add_parser("client.session.compact")
    compact_cmd.add_argument("session_spec_path")
    compact_cmd.add_argument("--compaction-policy-id", required=True)

    args = parser.parse_args()
    repo_root = _repo_root(str(args.repo_root))
    surface = str(args.surface)

    if args.command == "client.session.stage":
        result = surface_stage_status(
            surface=surface,
            repo_root=repo_root,
            session_spec_path=str(args.session_spec_path),
        )
    elif args.command == "client.session.abort":
        result = surface_abort_session(
            surface=surface,
            repo_root=repo_root,
            session_spec_path=str(args.session_spec_path),
            stage_id=str(args.stage_id),
            reason=str(args.reason),
        )
    elif args.command == "client.session.resume":
        result = surface_resume_session(
            surface=surface,
            repo_root=repo_root,
            session_spec_path=str(args.session_spec_path),
            bundle_id=str(args.bundle),
            lockfile_path=str(args.lockfile),
            registries_dir=str(args.registries_dir),
        )
    elif args.command == "client.session.compact":
        result = surface_compact_session(
            surface=surface,
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
