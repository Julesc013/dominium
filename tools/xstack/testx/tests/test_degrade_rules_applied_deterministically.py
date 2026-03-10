"""FAST test: CAP-NEG-3 degrade ladders apply deterministically."""

from __future__ import annotations


TEST_ID = "test_degrade_rules_applied_deterministically"
TEST_TAGS = ["fast", "compat", "cap_neg", "degrade"]


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg3_testlib import compiled_fallback_negotiation

    first = compiled_fallback_negotiation(repo_root)
    second = compiled_fallback_negotiation(repo_root)
    if str(first.get("negotiation_record_hash", "")) != str(second.get("negotiation_record_hash", "")):
        return {"status": "fail", "message": "degrade ladder negotiation hash drifted across identical runs"}
    return {"status": "pass", "message": "degrade ladders apply deterministically"}
