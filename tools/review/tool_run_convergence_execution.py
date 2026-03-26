#!/usr/bin/env python3
"""Run deterministic XI-4 convergence execution planning and logging."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.convergence_execution_common import (  # noqa: E402
    XiInputMissingError,
    build_convergence_execution_snapshot,
    write_convergence_execution_snapshot,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic XI-4 convergence execution logging.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    try:
        snapshot = build_convergence_execution_snapshot(args.repo_root)
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

    write_convergence_execution_snapshot(args.repo_root, snapshot)
    log_payload = dict(snapshot.get("convergence_execution_log") or {})
    stdout_payload = {
        "entry_count": int(log_payload.get("entry_count", 0) or 0),
        "quarantined_cluster_count": int(log_payload.get("quarantined_cluster_count", 0) or 0),
        "result": "complete",
        "result_counts": dict(log_payload.get("result_counts") or {}),
    }
    sys.stdout.write(json.dumps(stdout_payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
