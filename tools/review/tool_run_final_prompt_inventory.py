#!/usr/bin/env python3
"""Run deterministic PI-2 final prompt inventory generation."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.final_prompt_inventory_common import (  # noqa: E402
    build_final_prompt_inventory_snapshot,
    write_final_prompt_inventory_snapshot,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic PI-2 final prompt inventory generation.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    snapshot = build_final_prompt_inventory_snapshot(args.repo_root)
    write_final_prompt_inventory_snapshot(args.repo_root, snapshot)
    inventory = dict(snapshot.get("final_prompt_inventory") or {})
    summary = dict(inventory.get("summary") or {})
    payload = {
        "critical_path_prompt_count": int(summary.get("critical_path_prompt_count", 0) or 0),
        "parallelizable_prompt_count": int(summary.get("parallelizable_prompt_count", 0) or 0),
        "prompt_count": int(summary.get("prompt_count", 0) or 0),
        "result": "complete",
        "risk_row_count": len(list(dict(snapshot.get("prompt_risk_matrix") or {}).get("prompts") or [])),
        "strategy_fingerprint": str(inventory.get("deterministic_fingerprint", "")).strip(),
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
