"""FAST test: EARTH-9 cross-platform determinism hash matches the regression lock."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_earth_mvp_hash_match"
TEST_TAGS = ["fast", "earth", "hash", "cross_platform", "regression"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth9_testlib import earth_mvp_hash, earth_regression_baseline

    observed = str(earth_mvp_hash(repo_root)).strip().lower()
    baseline = earth_regression_baseline(repo_root)
    expected = str(baseline.get("cross_platform_determinism_hash", "")).strip().lower()
    if not expected:
        return {"status": "fail", "message": "EARTH-9 regression lock omitted cross_platform_determinism_hash"}
    if observed != expected:
        return {
            "status": "fail",
            "message": "EARTH-9 cross-platform hash drifted (expected {}, got {})".format(expected, observed or "<missing>"),
        }
    return {"status": "pass", "message": "EARTH-9 cross-platform determinism hash matches the regression lock"}
