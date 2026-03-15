"""FAST test: numeric discipline hash stays cross-platform stable."""

from __future__ import annotations


TEST_ID = "test_cross_platform_hash_match_for_numeric_ops"
TEST_TAGS = ["fast", "numeric", "cross_platform"]
EXPECTED_HASH = "79bfada564c9bebf91d6918343e8873be979829c56424e279713089febe2e280"


def run(repo_root: str):
    del repo_root
    from tools.xstack.testx.tests.numeric_discipline_testlib import numeric_ops_hash

    observed = numeric_ops_hash()
    if not EXPECTED_HASH:
        return {"status": "fail", "message": "numeric ops expected hash is not pinned"}
    if observed != EXPECTED_HASH:
        return {
            "status": "fail",
            "message": "numeric ops hash drifted: expected {} got {}".format(EXPECTED_HASH, observed),
        }
    return {"status": "pass", "message": "numeric ops hash matches the pinned cross-platform baseline"}
