#!/usr/bin/env python3
"""Run deterministic Xi-5x1 residual convergence reporting and validation."""

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


from tools.review.xi5x1_common import Xi5x1InputsMissing, run_xi5x1  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Xi-5x1 residual convergence reporting.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--write-only", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = run_xi5x1(args.repo_root, run_gates=not args.write_only)
    except Xi5x1InputsMissing as exc:
        sys.stdout.write(str(exc).strip())
        sys.stdout.write("\n")
        return 4

    postmove = dict(result.get("postmove_report") or {})
    gate_model = dict(result.get("gate_model") or {})
    execution_log = dict(result.get("execution_log") or {})
    payload = {
        "classified_rows": int(dict(result.get("classification_lock") or {}).get("row_count", 0) or 0),
        "executed_items": int(execution_log.get("executed_item_count", 0) or 0),
        "result": "complete",
        "remaining_rows": len(list(postmove.get("remaining_rows") or [])),
        "runtime_shadow_paths_remaining": list(postmove.get("dangerous_shadow_root_paths_remaining") or []),
        "xi6_ready": bool(gate_model.get("xi6_ready")),
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
