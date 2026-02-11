#!/usr/bin/env python3
"""Sanctioned RepoX wrapper that routes through gate.py."""

import os
import subprocess
import sys


def _repo_root():
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def main():
    repo_root = _repo_root()
    gate_script = os.path.join(repo_root, "scripts", "dev", "gate.py")
    cmd = [
        sys.executable,
        gate_script,
        "verify",
        "--repo-root",
        repo_root,
        "--only-gate",
        "repox.precheck",
        "--only-gate",
        "repox.full",
    ]
    return subprocess.run(cmd, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
