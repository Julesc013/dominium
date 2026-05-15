#!/usr/bin/env python3
"""Run AIDE wrapper commands from the repo command registry."""

from __future__ import annotations

import argparse
import sys
from typing import Dict

from wrappers import WrapperError, command_to_dict, dumps_json, load_commands, resolve_repo_root, run_command


def _load(repo_root_arg: str):
    repo_root = resolve_repo_root(repo_root_arg)
    commands = load_commands(repo_root)
    return repo_root, commands


def cmd_list(args: argparse.Namespace) -> int:
    repo_root, commands = _load(args.repo_root)
    if args.json:
        print(dumps_json({"repo_root": str(repo_root), "commands": [command_to_dict(commands[name]) for name in sorted(commands)]}))
        return 0
    for name in sorted(commands):
        spec = commands[name]
        print("{0}\t{1}\t{2}".format(name, spec.registry_status, spec.metadata.get("description", "")))
    return 0


def cmd_describe(args: argparse.Namespace) -> int:
    _repo_root, commands = _load(args.repo_root)
    if args.command_name not in commands:
        raise WrapperError("unknown command: {0}".format(args.command_name))
    spec = commands[args.command_name]
    data = command_to_dict(spec)
    if args.json:
        print(dumps_json(data))
        return 0
    print("command: {0}".format(spec.name))
    print("status: {0}".format(spec.registry_status))
    print("description: {0}".format(spec.metadata.get("description", "")))
    print("family: {0}".format(spec.metadata.get("family", "")))
    print("underlying: {0}".format(" ".join(spec.underlying)))
    print("execution_allowed: {0}".format(spec.execution_allowed))
    print("apply_allowed: {0}".format(spec.apply_allowed))
    print("network_allowed: {0}".format(spec.network_allowed))
    print("writes_allowed: {0}".format(bool(spec.metadata.get("writes_allowed", False))))
    print("timeout_seconds: {0}".format(spec.timeout_seconds))
    print("contract: {0}".format(spec.contract_path))
    return 0


def _print_run_result(result: Dict[str, object]) -> None:
    print("command: {0}".format(result["command"]))
    print("dry_run: {0}".format(result["dry_run"]))
    print("returncode: {0}".format(result["returncode"]))
    print("underlying: {0}".format(" ".join(result["underlying"])))
    stdout = str(result.get("stdout", ""))
    stderr = str(result.get("stderr", ""))
    if stdout:
        print("stdout:")
        print(stdout.rstrip())
    if stderr:
        print("stderr:")
        print(stderr.rstrip())


def cmd_run(args: argparse.Namespace) -> int:
    repo_root, commands = _load(args.repo_root)
    if args.command_name not in commands:
        raise WrapperError("unknown command: {0}".format(args.command_name))
    result = run_command(repo_root, commands[args.command_name], dry_run=args.dry_run)
    if args.json:
        print(dumps_json(result))
    else:
        _print_run_result(result)
    return int(result["returncode"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AIDE wrapper commands.")
    parser.add_argument("--repo-root", default=".", help="Repository root containing .aide and .git.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List registered AIDE wrapper commands.")
    list_parser.add_argument("--json", action="store_true", help="Emit JSON.")
    list_parser.set_defaults(func=cmd_list)

    describe_parser = subparsers.add_parser("describe", help="Describe a wrapper command.")
    describe_parser.add_argument("command_name")
    describe_parser.add_argument("--json", action="store_true", help="Emit JSON.")
    describe_parser.set_defaults(func=cmd_describe)

    run_parser = subparsers.add_parser("run", help="Run or dry-run a wrapper command.")
    run_parser.add_argument("command_name")
    run_parser.add_argument("--dry-run", action="store_true", help="Print the underlying command without executing it.")
    run_parser.add_argument("--json", action="store_true", help="Emit JSON.")
    run_parser.set_defaults(func=cmd_run)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except WrapperError as exc:
        print("ERROR: {0}".format(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
