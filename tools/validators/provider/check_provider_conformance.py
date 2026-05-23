#!/usr/bin/env python3
"""Run provider/service conformance contract checks."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    command = [
        sys.executable,
        "tools/validators/contracts/check_service_conformance.py",
        "--repo-root",
        ".",
        "--fixtures",
    ]
    if args.strict:
        command.append("--strict")
    result = subprocess.run(command, cwd=str(repo_root), check=False)
    return int(result.returncode)


if __name__ == "__main__":
    sys.exit(main())
