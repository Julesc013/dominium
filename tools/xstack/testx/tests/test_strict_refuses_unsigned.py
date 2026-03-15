"""FAST test: strict trust policy refuses unsigned artifacts."""

from __future__ import annotations


TEST_ID = "test_strict_refuses_unsigned"
TEST_TAGS = ["fast", "security", "trust", "strict"]


def run(repo_root: str):
    from src.security.trust import REFUSAL_TRUST_SIGNATURE_MISSING
    from tools.xstack.testx.tests.trust_model_testlib import strict_unsigned

    result = strict_unsigned(repo_root)
    if str(result.get("refusal_code", "")).strip() != REFUSAL_TRUST_SIGNATURE_MISSING:
        return {"status": "fail", "message": "strict trust policy must refuse unsigned governed artifacts"}
    return {"status": "pass", "message": "strict trust policy refuses unsigned artifacts"}
