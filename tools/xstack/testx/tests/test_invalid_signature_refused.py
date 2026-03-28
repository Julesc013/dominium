"""FAST test: invalid signatures are refused deterministically."""

from __future__ import annotations


TEST_ID = "test_invalid_signature_refused"
TEST_TAGS = ["fast", "security", "trust", "signature"]


def run(repo_root: str):
    from security.trust import REFUSAL_TRUST_SIGNATURE_INVALID
    from tools.xstack.testx.tests.trust_model_testlib import invalid_signature

    result = invalid_signature(repo_root)
    if str(result.get("refusal_code", "")).strip() != REFUSAL_TRUST_SIGNATURE_INVALID:
        return {"status": "fail", "message": "invalid signatures must be refused deterministically"}
    return {"status": "pass", "message": "invalid signatures are refused"}
