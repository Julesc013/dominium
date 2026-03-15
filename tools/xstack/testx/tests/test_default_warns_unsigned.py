"""FAST test: default mock trust policy warns but does not refuse unsigned artifacts."""

from __future__ import annotations


TEST_ID = "test_default_warns_unsigned"
TEST_TAGS = ["fast", "security", "trust", "default"]


def run(repo_root: str):
    from tools.xstack.testx.tests.trust_model_testlib import default_unsigned

    result = default_unsigned(repo_root)
    warning_codes = {
        str(dict(row or {}).get("code", "")).strip()
        for row in list(result.get("warnings") or [])
        if str(dict(row or {}).get("code", "")).strip()
    }
    if str(result.get("result", "")).strip() not in {"complete", "warn"}:
        return {"status": "fail", "message": "default mock trust policy must not refuse unsigned artifacts"}
    if "warn.trust.signature_missing" not in warning_codes:
        return {"status": "fail", "message": "default mock trust policy must emit warn.trust.signature_missing"}
    return {"status": "pass", "message": "default mock trust policy warns on unsigned artifacts"}
