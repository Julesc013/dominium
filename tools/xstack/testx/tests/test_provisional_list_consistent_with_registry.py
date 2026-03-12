"""FAST test: the release provisional tracker matches current registry stability data."""

from __future__ import annotations


TEST_ID = "test_provisional_list_consistent_with_registry"
TEST_TAGS = ["fast", "release", "scope_freeze", "provisional"]


def run(repo_root: str):
    from tools.xstack.testx.tests.scope_freeze_testlib import provisional_feature_list_mismatch

    mismatch = provisional_feature_list_mismatch(repo_root)
    if mismatch:
        return {"status": "fail", "message": mismatch}
    return {"status": "pass", "message": "provisional feature tracker matches current registry stability markers"}
