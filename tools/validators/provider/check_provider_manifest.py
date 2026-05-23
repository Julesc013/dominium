#!/usr/bin/env python3
"""Run provider manifest, provider structure, and profile reference checks."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence


def run(repo_root: Path, argv: list[str]) -> int:
    result = subprocess.run(argv, cwd=str(repo_root), check=False)
    return int(result.returncode)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    strict = ["--strict"] if args.strict else []
    commands = [
        [sys.executable, "tools/validators/contracts/check_provider_model.py", "--repo-root", ".", "--fixtures"] + strict,
        [sys.executable, "tools/validators/repo/check_provider_structure.py", "--repo-root", "."] + strict,
    ]
    failures = 0
    for command in commands:
        if run(repo_root, command) != 0:
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
