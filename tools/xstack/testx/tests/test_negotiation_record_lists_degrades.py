"""FAST test: negotiation record lists disabled and substituted capabilities."""

from __future__ import annotations


TEST_ID = "test_negotiation_record_lists_degrades"
TEST_TAGS = ["fast", "compat", "cap_neg", "degrade"]


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg3_testlib import compiled_fallback_negotiation

    result = compiled_fallback_negotiation(repo_root)
    record = dict(result.get("negotiation_record") or {})
    disabled = list(record.get("disabled_capabilities") or [])
    substituted = list(record.get("substituted_capabilities") or [])
    if not disabled:
        return {"status": "fail", "message": "negotiation record is missing disabled capabilities"}
    if not substituted:
        return {"status": "fail", "message": "negotiation record is missing substituted capabilities"}
    return {"status": "pass", "message": "negotiation record lists explicit degrade rows"}
