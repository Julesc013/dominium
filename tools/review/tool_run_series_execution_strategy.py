#!/usr/bin/env python3
"""Run deterministic PI-1 series execution strategy generation."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.series_execution_strategy_common import (  # noqa: E402
    build_series_execution_strategy_snapshot,
    write_series_execution_strategy_snapshot,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic PI-1 series execution strategy generation.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    snapshot = build_series_execution_strategy_snapshot(args.repo_root)
    write_series_execution_strategy_snapshot(args.repo_root, snapshot)
    strategy = dict(snapshot.get("series_execution_strategy") or {})
    payload = {
        "capability_count": len(list(strategy.get("capability_foundations") or [])),
        "phase_count": len(list(dict(snapshot.get("foundation_phases") or {}).get("phases") or [])),
        "result": "complete",
        "review_gate_count": len(list(dict(snapshot.get("manual_review_gates") or {}).get("gates") or [])),
        "strategy_fingerprint": str(strategy.get("deterministic_fingerprint", "")).strip(),
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
