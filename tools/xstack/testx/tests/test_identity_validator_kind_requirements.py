"""FAST test: UNIVERSAL-ID0 validator enforces required fields per identity kind."""

from __future__ import annotations


TEST_ID = "test_identity_validator_kind_requirements"
TEST_TAGS = ["fast", "meta", "identity", "validator"]


def run(repo_root: str):
    from tools.xstack.testx.tests.identity_testlib import invalid_pack_identity_validation

    report = invalid_pack_identity_validation(repo_root)
    codes = {str(dict(row or {}).get("code", "")).strip() for row in list(report.get("errors") or [])}
    if "identity_kind_missing_required_field" not in codes:
        return {"status": "fail", "message": "pack identity without semver must fail required-field validation"}
    return {"status": "pass", "message": "identity validator enforces per-kind required fields"}
