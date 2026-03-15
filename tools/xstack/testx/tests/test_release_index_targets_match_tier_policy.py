"""FAST test: release-index targets resolve to declared Tier 1/2 rows only."""

from __future__ import annotations


TEST_ID = "test_release_index_targets_match_tier_policy"
TEST_TAGS = ["fast", "release", "platform", "arch-matrix"]


def run(repo_root: str):
    from tools.xstack.testx.tests.arch_matrix_testlib import build_report

    report = build_report(repo_root)
    expected_ids = {
        str(dict(row).get("target_id", "")).strip()
        for row in list(report.get("expected_release_index_targets") or [])
        if str(dict(row).get("target_id", "")).strip()
    }
    actual_rows = []
    for entry in list(report.get("release_index_rows") or []):
        actual_rows.extend(list(dict(entry or {}).get("platform_rows") or []))
    if not actual_rows:
        return {"status": "fail", "message": "ARCH-MATRIX report must expose at least one release-index platform row"}
    for row in actual_rows:
        row_map = dict(row or {})
        target_id = str(row_map.get("target_id", "")).strip()
        tier = int(row_map.get("tier", 0) or 0)
        if not target_id:
            return {"status": "fail", "message": "release-index row is not mapped to a declared target"}
        if tier > 2 or tier <= 0:
            return {"status": "fail", "message": "release-index row '{}' violates Tier 1/2 policy".format(target_id)}
        if expected_ids and target_id not in expected_ids:
            return {"status": "fail", "message": "release-index row '{}' is not in the expected default target set".format(target_id)}
    return {"status": "pass", "message": "release-index rows match Tier policy"}
