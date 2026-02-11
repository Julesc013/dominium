#!/usr/bin/env python3
"""Sanctioned TestX wrapper that routes through gate.py or canonical ctest mode."""

import argparse
import os
import shlex
import shutil
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
        "testx.verify",
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
    def _resolve_ctest():
        cache_candidates = []
        if args.test_dir:
            candidate = args.test_dir
            if not os.path.isabs(candidate):
                candidate = os.path.join(repo_root, candidate)
            cache_candidates.append(os.path.join(candidate, "CMakeCache.txt"))
        for cache_path in cache_candidates:
            if not os.path.isfile(cache_path):
                continue
            try:
                with open(cache_path, "r", encoding="utf-8", errors="ignore") as handle:
                    for line in handle:
                        if line.startswith("CMAKE_CTEST_COMMAND:INTERNAL="):
                            value = line.split("=", 1)[1].strip()
                            if value and os.path.isfile(value):
                                return value
            except OSError:
                continue

        resolved = shutil.which("ctest", path=env.get("PATH", ""))
        if resolved:
            return resolved

        cmake_cmd = shutil.which("cmake", path=env.get("PATH", ""))
        if cmake_cmd:
            probe = os.path.join(os.path.dirname(cmake_cmd), "ctest.exe" if os.name == "nt" else "ctest")
            if os.path.isfile(probe):
                return probe
        return ""

    ctest_cmd = _resolve_ctest()
    if not ctest_cmd:
        sys.stderr.write("refuse.ctest_unresolvable: unable to resolve ctest in canonical environment\n")
        return 127

    cmd = [ctest_cmd]
    if args.preset:
        cmd.extend(["--preset", args.preset])
    if args.test_dir:
        cmd.extend(["--test-dir", args.test_dir])
    if args.config:
        cmd.extend(["-C", args.config])
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
    parser.add_argument("--config", default="Debug")
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
