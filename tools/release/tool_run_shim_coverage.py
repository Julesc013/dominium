#!/usr/bin/env python3
"""Generate the REPO-LAYOUT-1 shim coverage report."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.release.shim_coverage_common import write_shim_coverage_report  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    report = write_shim_coverage_report(repo_root)
    print(
        json.dumps(
            {
                "result": str(report.get("result", "")).strip(),
                "violation_count": int(len(list(report.get("violations") or []))),
                "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not list(report.get("violations") or []) else 1


if __name__ == "__main__":
    raise SystemExit(main())
