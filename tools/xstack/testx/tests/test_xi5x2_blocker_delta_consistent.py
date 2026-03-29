from __future__ import annotations

from tools.xstack.testx.tests.xi5x2_testlib import committed_blocker_delta

TEST_ID = "test_xi5x2_blocker_delta_consistent"
TEST_TAGS = ["fast", "xi5x2", "restructure"]


def run(repo_root: str):
    payload = committed_blocker_delta(repo_root)
    before_counts = dict(payload.get("before_counts") or {})
    after_counts = dict(payload.get("after_counts") or {})
    resolved_row_count = int(payload.get("resolved_row_count", 0) or 0)
    unchanged_row_count = int(payload.get("unchanged_row_count", 0) or 0)
    before_total = sum(int(value or 0) for value in before_counts.values())
    after_total = sum(int(value or 0) for value in after_counts.values())
    if before_total != resolved_row_count + unchanged_row_count:
        return {"status": "fail", "message": "Xi-5x2 blocker delta total mismatch"}
    if after_total != unchanged_row_count:
        return {"status": "fail", "message": "Xi-5x2 blocker delta after-count mismatch"}
    return {"status": "pass", "message": "Xi-5x2 blocker delta counts are internally consistent"}
