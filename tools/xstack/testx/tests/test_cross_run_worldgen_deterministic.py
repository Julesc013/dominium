"""FAST test: repeated Omega worldgen lock snapshot generation is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_run_worldgen_deterministic"
TEST_TAGS = ["fast", "worldgen", "lock", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.worldgen.worldgen_lock_common import build_worldgen_lock_snapshot, read_worldgen_baseline_seed

    seed_text = read_worldgen_baseline_seed(repo_root)
    first = build_worldgen_lock_snapshot(repo_root, seed_text=seed_text)
    second = build_worldgen_lock_snapshot(repo_root, seed_text=seed_text)
    if first != second:
        return {"status": "fail", "message": "worldgen lock snapshot diverged across repeated runs"}
    return {
        "status": "pass",
        "message": "worldgen lock snapshot stable across repeated runs ({})".format(
            str((first.get("record") or {}).get("deterministic_fingerprint", "")).strip() or "missing-fingerprint"
        ),
    }
