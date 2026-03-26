#!/usr/bin/env python3
"""Run deterministic XI-4z metadata consistency repair."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.xi4z_fix_common import (  # noqa: E402
    Xi4zFixInputsMissing,
    artifact_hashes,
    build_xi4z_fix_snapshot,
    write_xi4z_fix_snapshot,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic XI-4z metadata consistency repair.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    try:
        first = build_xi4z_fix_snapshot(args.repo_root)
        second = build_xi4z_fix_snapshot(args.repo_root)
    except Xi4zFixInputsMissing as exc:
        sys.stdout.write(str(exc).strip())
        sys.stdout.write("\n")
        return 4

    first_hashes = artifact_hashes(first)
    second_hashes = artifact_hashes(second)
    if first_hashes != second_hashes:
        sys.stdout.write(
            json.dumps(
                {
                    "code": "refusal.xi4zfix.validation_failed",
                    "first_hashes": first_hashes,
                    "reason": "nondeterministic_fix_outputs",
                    "second_hashes": second_hashes,
                },
                indent=2,
                sort_keys=True,
            )
        )
        sys.stdout.write("\n")
        return 3

    summary = dict(first.get("summary") or {})
    if bool(summary.get("mapping_decisions_changed")):
        sys.stdout.write(
            json.dumps(
                {
                    "code": "refusal.xi4zfix.validation_failed",
                    "reason": "mapping_decisions_changed",
                },
                indent=2,
                sort_keys=True,
            )
        )
        sys.stdout.write("\n")
        return 2
    if int(summary.get("remaining_mismatches_count", 0) or 0) != 0:
        sys.stdout.write(
            json.dumps(
                {
                    "code": "refusal.xi4zfix.validation_failed",
                    "reason": "remaining_path_inconsistency",
                },
                indent=2,
                sort_keys=True,
            )
        )
        sys.stdout.write("\n")
        return 2

    write_xi4z_fix_snapshot(args.repo_root, first)
    payload = {
        "files_changed_count": int(summary.get("files_changed_count", 0) or 0),
        "mapping_decisions_changed": False,
        "remaining_mismatches_count": 0,
        "result": "complete",
        "selected_option": str(summary.get("selected_option", "")).strip(),
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
