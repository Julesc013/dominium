#!/usr/bin/env python3
"""Run deterministic Π-0 meta-blueprint artifact generation."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.abspath(THIS_DIR)
for _repo_root_probe_depth in range(16):
    if os.path.exists(os.path.join(REPO_ROOT_HINT, "AGENTS.md")):
        break
    parent = os.path.dirname(REPO_ROOT_HINT)
    if parent == REPO_ROOT_HINT:
        REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
        break
    REPO_ROOT_HINT = parent
REPO_ROOT_HINT = os.path.normpath(REPO_ROOT_HINT)
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.audit.review.meta_blueprint_common import (  # noqa: E402
    build_meta_blueprint_snapshot,
    write_meta_blueprint_snapshot,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Π-0 meta-blueprint artifact generation.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    snapshot = build_meta_blueprint_snapshot(args.repo_root)
    write_meta_blueprint_snapshot(args.repo_root, snapshot)
    payload = {
        "capability_count": len(list(dict(snapshot.get("capability_dependency_graph") or {}).get("capabilities") or [])),
        "pipe_dream_count": len(list(dict(snapshot.get("pipe_dreams_matrix") or {}).get("rows") or [])),
        "readiness_row_count": len(list(dict(snapshot.get("readiness_matrix") or {}).get("rows") or [])),
        "result": "complete",
        "series_count": len(list(dict(snapshot.get("series_dependency_graph") or {}).get("series") or [])),
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
