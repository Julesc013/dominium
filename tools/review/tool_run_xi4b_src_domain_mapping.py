#!/usr/bin/env python3
"""Run deterministic XI-4b src-domain mapping and review bundle generation."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.xi4b_src_domain_mapping_common import (  # noqa: E402
    TMP_BUNDLE_REL,
    artifact_hashes,
    build_xi4b_snapshot,
    write_xi4b_snapshot,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic XI-4b src-domain mapping review generation.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    first = build_xi4b_snapshot(args.repo_root)
    second = build_xi4b_snapshot(args.repo_root)
    first_hashes = artifact_hashes(first)
    second_hashes = artifact_hashes(second)
    if first_hashes != second_hashes:
        sys.stdout.write(
            json.dumps(
                {
                    "result": "error",
                    "reason": "nondeterministic_output",
                    "first_hashes": first_hashes,
                    "second_hashes": second_hashes,
                },
                indent=2,
                sort_keys=True,
            )
        )
        sys.stdout.write("\n")
        return 3

    write_xi4b_snapshot(args.repo_root, first)
    summary = dict(first.get("summary") or {})
    payload = {
        "bundle_relpath": TMP_BUNDLE_REL,
        "conflict_count": int(summary.get("conflict_count", 0) or 0),
        "high_confidence_count": int(summary.get("high_confidence_count", 0) or 0),
        "mapping_count": int(summary.get("mapping_count", 0) or 0),
        "preferred_option": str(summary.get("preferred_option", "")).strip(),
        "result": "complete",
        "runtime_critical_blockers": int(summary.get("runtime_critical_blockers", 0) or 0),
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
