#!/usr/bin/env python3
"""Run deterministic XI-2 implementation scoring."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.implementation_scoring_common import (  # noqa: E402
    XiInputMissingError,
    build_implementation_scoring_snapshot,
    write_implementation_scoring_snapshot,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic XI-2 implementation scoring.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    try:
        snapshot = build_implementation_scoring_snapshot(args.repo_root)
    except XiInputMissingError as exc:
        sys.stdout.write(
            json.dumps(
                {
                    "result": "refused",
                    "refusal_code": exc.refusal_code,
                    "missing_inputs": list(exc.missing_paths),
                    "remediation": exc.remediation,
                },
                indent=2,
                sort_keys=True,
            )
        )
        sys.stdout.write("\n")
        return 2

    write_implementation_scoring_snapshot(args.repo_root, snapshot)
    stdout_payload = {
        "cluster_count": int(dict(snapshot.get("duplicate_cluster_rankings") or {}).get("cluster_count", 0) or 0),
        "implementation_count": int(dict(snapshot.get("implementation_scores") or {}).get("implementation_count", 0) or 0),
        "result": "complete",
        "unique_candidate_count": int(dict(snapshot.get("implementation_scores") or {}).get("unique_candidate_count", 0) or 0),
    }
    sys.stdout.write(json.dumps(stdout_payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
