#!/usr/bin/env python3
"""Run deterministic XI-4z package-collision normalization."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.xi4z_fix2_common import (  # noqa: E402
    Xi4zFix2InputsMissing,
    artifact_hashes,
    build_xi4z_fix2_snapshot,
    write_xi4z_fix2_snapshot,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic XI-4z package-collision normalization.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    try:
        first = build_xi4z_fix2_snapshot(args.repo_root)
        second = build_xi4z_fix2_snapshot(args.repo_root)
    except Xi4zFix2InputsMissing as exc:
        sys.stdout.write(str(exc).strip())
        sys.stdout.write("\n")
        return 4

    first_hashes = artifact_hashes(first)
    second_hashes = artifact_hashes(second)
    if first_hashes != second_hashes:
        sys.stdout.write(
            json.dumps(
                {
                    "code": "refusal.xi4zfix2.validation_failed",
                    "first_hashes": first_hashes,
                    "reason": "nondeterministic_fix2_outputs",
                    "second_hashes": second_hashes,
                },
                indent=2,
                sort_keys=True,
            )
        )
        sys.stdout.write("\n")
        return 3

    summary = dict(first.get("summary") or {})
    if int(summary.get("remaining_ambiguous_rows_count", 0) or 0) != 0:
        sys.stdout.write(
            json.dumps(
                {
                    "code": "refusal.xi4zfix2.validation_failed",
                    "reason": "approved_rows_still_ambiguous",
                },
                indent=2,
                sort_keys=True,
            )
        )
        sys.stdout.write("\n")
        return 2

    write_xi4z_fix2_snapshot(args.repo_root, first)
    payload = {
        "approved_for_xi5_count": int(summary.get("approved_for_xi5_count", 0) or 0),
        "approved_to_attic_count": int(summary.get("approved_to_attic_count", 0) or 0),
        "collision_package_count": int(summary.get("collision_package_count", 0) or 0),
        "collision_row_count": int(summary.get("collision_row_count", 0) or 0),
        "remaining_ambiguous_rows_count": 0,
        "result": "complete",
        "selected_option": str(summary.get("selected_option", "")).strip(),
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
