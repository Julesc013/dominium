#!/usr/bin/env python3
"""Run deterministic XI-3 convergence planning."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.convergence_plan_common import (  # noqa: E402
    XiInputMissingError,
    build_convergence_plan_snapshot,
    write_convergence_plan_snapshot,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic XI-3 convergence planning.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    try:
        snapshot = build_convergence_plan_snapshot(args.repo_root)
    except XiInputMissingError as exc:
        sys.stdout.write(
            json.dumps(
                {
                    "missing_inputs": list(exc.missing_paths),
                    "refusal_code": exc.refusal_code,
                    "remediation": exc.remediation,
                    "result": "refused",
                },
                indent=2,
                sort_keys=True,
            )
        )
        sys.stdout.write("\n")
        return 2

    write_convergence_plan_snapshot(args.repo_root, snapshot)
    payload = {
        "action_count": int(dict(snapshot.get("convergence_actions") or {}).get("action_count", 0) or 0),
        "cluster_count": int(dict(snapshot.get("convergence_plan") or {}).get("cluster_count", 0) or 0),
        "result": "complete",
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
