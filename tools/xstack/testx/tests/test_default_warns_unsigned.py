"""FAST test: default mock trust warns on unsigned release_index fixtures."""

from __future__ import annotations


TEST_ID = "test_default_warns_unsigned"
TEST_TAGS = ["fast", "omega", "trust", "default"]


def run(repo_root: str):
    from tools.xstack.testx.tests.trust_strict_testlib import build_report, case_by_id

    report = build_report(repo_root)
    case = case_by_id(report, "default_mock_accepts_unsigned_release_index")
    if str(case.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "default mock trust case no longer completes"}
    warning_codes = list(dict(case.get("details") or {}).get("warning_codes") or [])
    if "warn.trust.signature_missing" not in warning_codes:
        return {"status": "fail", "message": "default mock trust must emit warn.trust.signature_missing"}
    return {"status": "pass", "message": "default mock trust warns on unsigned release_index fixtures"}
