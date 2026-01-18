#!/usr/bin/env python3
from __future__ import print_function

import argparse
import os
import subprocess
import sys


def repo_root_from_script():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


def find_validate_all(repo_root):
    candidates = [
        os.path.join(repo_root, "build", "msvc-base", "bin", "validate_all.exe"),
        os.path.join(repo_root, "build", "msvc-base", "bin", "validate_all"),
        os.path.join(repo_root, "build", "bin", "validate_all.exe"),
        os.path.join(repo_root, "build", "bin", "validate_all"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def main():
    parser = argparse.ArgumentParser(description="Run unified governance validation (GOV0).")
    parser.add_argument("--repo-root", default=None, help="Repository root path")
    parser.add_argument("--exe", default=None, help="Path to validate_all executable")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--json-out", default=None, help="Optional JSON report path")
    parser.add_argument("--text-out", default=None, help="Optional text report path")
    args = parser.parse_args()

    repo_root = args.repo_root or repo_root_from_script()
    exe_path = args.exe or find_validate_all(repo_root)
    if not exe_path:
        print("validate_all executable not found.")
        print("Build it and rerun, or pass --exe=<path>.")
        return 2

    cmd = [exe_path, "--repo-root=" + repo_root, "--strict=" + ("1" if args.strict else "0")]
    if args.json_out:
        cmd.append("--json-out=" + args.json_out)
    if args.text_out:
        cmd.append("--text-out=" + args.text_out)
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main())
