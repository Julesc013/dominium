#!/usr/bin/env python3
"""Run deterministic Ξ-0 repository archaeology and architecture graph synthesis."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.architecture_graph_bootstrap_common import (  # noqa: E402
    build_architecture_snapshot,
    write_architecture_snapshot,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Ξ-0 repository archaeology and architecture graph synthesis.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    snapshot = build_architecture_snapshot(args.repo_root)
    write_architecture_snapshot(args.repo_root, snapshot)
    stdout_payload = {
        "result": "complete",
        "module_count": len(list(dict(snapshot.get("module_registry") or {}).get("modules") or [])),
        "symbol_count": len(list(dict(snapshot.get("symbol_index") or {}).get("symbols") or [])),
        "include_edge_count": len(list(dict(snapshot.get("include_graph") or {}).get("edges") or [])),
        "build_target_count": len(list(dict(snapshot.get("build_graph") or {}).get("targets") or [])),
        "architecture_fingerprint": str(dict(snapshot.get("architecture_graph") or {}).get("deterministic_fingerprint", "")).strip(),
    }
    sys.stdout.write(json.dumps(stdout_payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
