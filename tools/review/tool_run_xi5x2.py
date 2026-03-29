#!/usr/bin/env python3
"""Run deterministic Xi-5x2 residual convergence reporting."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.import_bridge import install_src_aliases  # noqa: E402

install_src_aliases(REPO_ROOT_HINT)


from tools.review.xi5x2_common import Xi5x2InputsMissing, run_xi5x2  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Xi-5x2 residual convergence reporting.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--write-only", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = run_xi5x2(args.repo_root, run_gates=not args.write_only)
    except Xi5x2InputsMissing as exc:
        sys.stdout.write(str(exc).strip())
        sys.stdout.write("\n")
        return 4

    classification_lock = dict(result.get("classification_lock") or {})
    execution_log = dict(result.get("execution_log") or {})
    postmove = dict(result.get("postmove_report") or {})
    gate_model = dict(result.get("gate_model") or {})
    blocker_delta = dict(result.get("blocker_delta") or {})
    payload = {
        "classified_rows": int(classification_lock.get("row_count", 0) or 0),
        "executed_items": int(execution_log.get("executed_item_count", 0) or 0),
        "remaining_rows": len(list(postmove.get("remaining_rows") or [])),
        "result": "complete",
        "runtime_shadow_paths_remaining": list(postmove.get("dangerous_shadow_root_paths_remaining") or []),
        "xi6_ready": bool(gate_model.get("xi6_ready")),
        "resolved_rows": int(blocker_delta.get("resolved_row_count", 0) or 0),
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
