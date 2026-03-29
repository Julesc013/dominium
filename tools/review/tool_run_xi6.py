#!/usr/bin/env python3
"""Run deterministic Xi-6 architecture freeze generation and validation."""

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


from tools.review.xi6_common import Xi6InputsMissing, run_xi6  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Xi-6 architecture freeze generation and validation.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--write-only", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = run_xi6(args.repo_root, run_gates=not args.write_only)
    except Xi6InputsMissing as exc:
        sys.stdout.write(str(exc).strip())
        sys.stdout.write("\n")
        return 4

    payload = {
        "engine_count": len(list(dict(result.get("single_engine_registry") or {}).get("engines") or [])),
        "gate_failures": len([row for row in list(result.get("gate_runs") or []) if str(dict(row or {}).get("status")) != "pass"]),
        "module_count": len(list(dict(result.get("architecture_graph_v1") or {}).get("modules") or [])),
        "result": str(result.get("result", "")).strip() or "blocked",
        "single_engine_findings": len(list(result.get("single_engine_findings") or [])),
        "ui_truth_leak_findings": len(list(result.get("ui_truth_leak_findings") or [])),
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0 if payload["result"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
