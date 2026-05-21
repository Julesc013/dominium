#!/usr/bin/env python3
"""Run doctrine recovery matrix contract validation."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    command = [
        sys.executable,
        "-B",
        str(repo_root / "tools/validators/contracts/check_doctrine_recovery_matrix.py"),
        "--repo-root",
        str(repo_root),
        "--strict",
        "--fixtures",
    ]
    completed = subprocess.run(command, cwd=str(repo_root))
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
