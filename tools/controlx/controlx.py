#!/usr/bin/env python3
"""ControlX CLI entrypoint."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

CORE_DIR = os.path.join(THIS_DIR, "core")
if CORE_DIR not in sys.path:
    sys.path.insert(0, CORE_DIR)

DEV_SCRIPT_DIR = os.path.normpath(os.path.join(THIS_DIR, "..", "..", "scripts", "dev"))
if DEV_SCRIPT_DIR not in sys.path:
    sys.path.insert(0, DEV_SCRIPT_DIR)


from queue_runner import load_policy, run_items, run_queue_file
from prompt_parser import parse_prompt
from prompt_sanitizer import sanitize_prompt


def _repo_root(path: str) -> str:
    if path:
        return os.path.abspath(path)
    return os.path.normpath(os.path.join(THIS_DIR, "..", ".."))


def _read_prompt_arg(args: argparse.Namespace) -> str:
    if args.prompt_text:
        return str(args.prompt_text)
    if not args.prompt_file:
        raise RuntimeError("refuse.prompt_missing")
    with open(args.prompt_file, "r", encoding="utf-8") as handle:
        return handle.read()


def _cmd_sanitize(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    policy = load_policy(repo_root, args.policy)
    prompt_text = _read_prompt_arg(args)
    parsed = parse_prompt(prompt_text, policy)
    sanitized = sanitize_prompt(parsed, policy)
    print(
        json.dumps(
            {
                "result": "sanitized",
                "prompt_hash": parsed.get("prompt_hash"),
                "sanitized_prompt": sanitized.get("sanitized_prompt"),
                "sanitization_actions": sanitized.get("actions", []),
                "execution_plan": sanitized.get("execution_plan", []),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    policy = load_policy(repo_root, args.policy)
    prompt_text = _read_prompt_arg(args)
    item: Dict[str, Any] = {"item_id": "controlx.run.0001", "prompt_text": prompt_text}
    result = run_items(
        repo_root=repo_root,
        items=[item],
        policy=policy,
        workspace_seed=args.workspace_id,
        dry_run=bool(args.dry_run),
        audit_root=args.audit_root,
        simulate_mechanical_failure_index=args.simulate_mechanical_failure_index,
    )
    print(json.dumps(result["payload"], indent=2, sort_keys=True))
    return int(result["returncode"])


def _cmd_run_queue(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    policy = load_policy(repo_root, args.policy)
    result = run_queue_file(
        repo_root=repo_root,
        queue_file=args.queue_file,
        policy=policy,
        workspace_seed=args.workspace_id,
        dry_run=bool(args.dry_run),
        audit_root=args.audit_root,
        simulate_mechanical_failure_index=args.simulate_mechanical_failure_index,
    )
    print(json.dumps(result["payload"], indent=2, sort_keys=True))
    return int(result["returncode"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ControlX orchestration kernel.")

    sub = parser.add_subparsers(dest="command", required=True)

    def add_common_arguments(sub_parser: argparse.ArgumentParser) -> None:
        sub_parser.add_argument("--repo-root", default="")
        sub_parser.add_argument(
            "--policy",
            default=os.path.join("data", "registries", "controlx_policy.json"),
            help="Policy registry path relative to repo root.",
        )

    sanitize = sub.add_parser("sanitize", help="Parse and sanitize a prompt.")
    add_common_arguments(sanitize)
    sanitize.add_argument("--prompt-file", default="")
    sanitize.add_argument("--prompt-text", default="")
    sanitize.set_defaults(func=_cmd_sanitize)

    run = sub.add_parser("run", help="Run a single prompt through ControlX.")
    add_common_arguments(run)
    run.add_argument("--prompt-file", default="")
    run.add_argument("--prompt-text", default="")
    run.add_argument("--workspace-id", default="")
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--audit-root", default=os.path.join("docs", "audit", "controlx"))
    run.add_argument("--simulate-mechanical-failure-index", type=int, default=0)
    run.set_defaults(func=_cmd_run)

    run_queue = sub.add_parser("run-queue", help="Run queued prompts through ControlX.")
    add_common_arguments(run_queue)
    run_queue.add_argument("--queue-file", required=True)
    run_queue.add_argument("--workspace-id", default="")
    run_queue.add_argument("--dry-run", action="store_true")
    run_queue.add_argument("--audit-root", default=os.path.join("docs", "audit", "controlx"))
    run_queue.add_argument("--simulate-mechanical-failure-index", type=int, default=0)
    run_queue.set_defaults(func=_cmd_run_queue)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
