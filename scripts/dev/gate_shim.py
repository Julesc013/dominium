#!/usr/bin/env python3
"""Legacy shim that forwards every invocation to gate.py."""

import os
import subprocess
import sys


def _repo_root():
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def main():
    repo_root = _repo_root()
    gate_script = os.path.join(repo_root, "scripts", "dev", "gate.py")
    args = list(sys.argv[1:])
    if "--repo-root" not in args:
        args.extend(["--repo-root", repo_root])
    cmd = [sys.executable, gate_script] + args
    return subprocess.run(cmd, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
