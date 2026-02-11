#!/usr/bin/env python3
"""Sanctioned TestX wrapper that routes through gate.py or canonical ctest mode."""

import argparse
import os
import shlex
import subprocess
import sys


def _repo_root(value):
    if value:
        return os.path.normpath(os.path.abspath(value))
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def _gate_mode(repo_root, workspace_id):
    gate_script = os.path.join(repo_root, "scripts", "dev", "gate.py")
    cmd = [
        sys.executable,
        gate_script,
        "exitcheck",
        "--repo-root",
        repo_root,
        "--only-gate",
        "testx.full",
    ]
    if workspace_id:
        cmd.extend(["--workspace-id", workspace_id])
    return subprocess.run(cmd, check=False).returncode


def _ctest_mode(repo_root, workspace_id, args):
    dev_root = os.path.join(repo_root, "scripts", "dev")
    if dev_root not in sys.path:
        sys.path.insert(0, dev_root)
    from env_tools_lib import canonicalize_env_for_workspace

    env, _ = canonicalize_env_for_workspace(dict(os.environ), repo_root, ws_id=workspace_id or "")
    cmd = ["ctest"]
    if args.preset:
        cmd.extend(["--preset", args.preset])
    if args.test_dir:
        cmd.extend(["--test-dir", args.test_dir])
    if args.output_on_failure:
        cmd.append("--output-on-failure")
    if args.include_regex:
        cmd.extend(["-R", args.include_regex])
    if args.exclude_regex:
        cmd.extend(["-E", args.exclude_regex])
    if args.extra_args:
        cmd.extend(shlex.split(args.extra_args, posix=(os.name != "nt")))
    return subprocess.run(cmd, cwd=repo_root, env=env, check=False).returncode


def build_parser():
    parser = argparse.ArgumentParser(description="Run TestX through canonical gate or wrapper mode.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--workspace-id", default="")
    parser.add_argument("--test-dir", default="")
    parser.add_argument("--preset", default="")
    parser.add_argument("--include-regex", default="")
    parser.add_argument("--exclude-regex", default="")
    parser.add_argument("--extra-args", default="")
    parser.add_argument("--output-on-failure", action="store_true")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    repo_root = _repo_root(args.repo_root)

    ctest_requested = bool(
        args.test_dir or args.preset or args.include_regex or args.exclude_regex or args.extra_args or args.output_on_failure
    )
    if ctest_requested:
        return _ctest_mode(repo_root, args.workspace_id, args)
    return _gate_mode(repo_root, args.workspace_id)


if __name__ == "__main__":
    raise SystemExit(main())
