#!/usr/bin/env python3
"""Compare two deterministic Ω-9 toolchain run directories."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.mvp.toolchain_matrix_common import compare_toolchain_runs  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--left-run-dir", required=True)
    parser.add_argument("--right-run-dir", required=True)
    parser.add_argument("--write-path", default="")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    report = compare_toolchain_runs(
        repo_root,
        str(args.left_run_dir),
        str(args.right_run_dir),
        write_path=str(args.write_path or ""),
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
