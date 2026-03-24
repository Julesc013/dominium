"""FAST test: committed worldgen baseline snapshot matches regeneration."""

from __future__ import annotations

import sys


TEST_ID = "test_worldgen_baseline_matches_snapshot"
TEST_TAGS = ["fast", "worldgen", "lock", "baseline"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.worldgen.worldgen_lock_common import verify_worldgen_lock

    report = verify_worldgen_lock(repo_root)
    if not bool(report.get("matches_snapshot")):
        mismatch = ", ".join(str(item).strip() for item in list(report.get("mismatched_fields") or [])[:4] if str(item).strip())
        return {
            "status": "fail",
            "message": "worldgen lock baseline drifted{}".format(": {}".format(mismatch) if mismatch else ""),
        }
    return {"status": "pass", "message": "worldgen lock baseline snapshot matches regeneration"}
