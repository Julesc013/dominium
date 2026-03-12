"""FAST test: the frozen semantic contract registry hash has not drifted."""

from __future__ import annotations


TEST_ID = "test_frozen_contract_hashes_unchanged"
TEST_TAGS = ["fast", "release", "scope_freeze", "contracts"]


def run(repo_root: str):
    from tools.xstack.testx.tests.scope_freeze_testlib import (
        current_frozen_contract_hash,
        expected_frozen_contract_hash,
    )

    current_hash = current_frozen_contract_hash(repo_root)
    expected_hash = expected_frozen_contract_hash()
    if current_hash != expected_hash:
        return {
            "status": "fail",
            "message": "semantic contract registry hash drifted: {} != {}".format(current_hash, expected_hash),
        }
    return {"status": "pass", "message": "semantic contract registry hash matches the frozen v0.0.0 value"}
