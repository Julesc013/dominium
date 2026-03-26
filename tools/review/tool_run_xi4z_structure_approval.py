#!/usr/bin/env python3
"""Run deterministic XI-4z structure approval and XI-5 readiness generation."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.xi4z_structure_approval_common import (  # noqa: E402
    TMP_BUNDLE_REL,
    Xi4zCoreInputsMissing,
    artifact_hashes,
    build_xi4z_snapshot,
    write_xi4z_snapshot,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic XI-4z structure approval generation.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    try:
        first = build_xi4z_snapshot(args.repo_root)
        second = build_xi4z_snapshot(args.repo_root)
    except Xi4zCoreInputsMissing as exc:
        sys.stdout.write(str(exc).strip())
        sys.stdout.write("\n")
        return 4

    first_hashes = artifact_hashes(first)
    second_hashes = artifact_hashes(second)
    if first_hashes != second_hashes:
        sys.stdout.write(
            json.dumps(
                {
                    "code": "refusal.xi4z.nondeterministic_output",
                    "first_hashes": first_hashes,
                    "reason": "nondeterministic_output",
                    "second_hashes": second_hashes,
                },
                indent=2,
                sort_keys=True,
            )
        )
        sys.stdout.write("\n")
        return 3

    write_xi4z_snapshot(args.repo_root, first)
    summary = dict(first.get("summary") or {})
    payload = {
        "approved_for_xi5_count": int(summary.get("approved_for_xi5_count", 0) or 0),
        "approved_to_attic_count": int(summary.get("approved_to_attic_count", 0) or 0),
        "bundle_relpath": TMP_BUNDLE_REL,
        "deferred_to_xi5b_count": int(summary.get("deferred_to_xi5b_count", 0) or 0),
        "result": "complete",
        "selected_option": str(summary.get("selected_option", "")).strip(),
        "total_rows": int(summary.get("total_rows", 0) or 0),
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
