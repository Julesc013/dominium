"""FAST test: baseline universe proof anchors match regeneration."""

from __future__ import annotations

import sys


TEST_ID = "test_baseline_proof_anchors_match"
TEST_TAGS = ["fast", "omega", "baseline_universe", "anchors"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.mvp.baseline_universe_common import verify_baseline_universe

    report = verify_baseline_universe(repo_root)
    if not bool(report.get("matches_snapshot")):
        mismatch = ", ".join(str(item).strip() for item in list(report.get("mismatched_fields") or [])[:6] if str(item).strip())
        return {
            "status": "fail",
            "message": "baseline universe proof anchors drifted{}".format(": {}".format(mismatch) if mismatch else ""),
        }
    return {"status": "pass", "message": "baseline universe proof anchors match regeneration"}
