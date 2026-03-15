"""FAST test: UNIVERSAL-ID0 block schema and baseline report are valid."""

from __future__ import annotations


TEST_ID = "test_identity_block_schema_valid"
TEST_TAGS = ["fast", "meta", "identity", "schema"]


def run(repo_root: str):
    from tools.xstack.testx.tests.identity_testlib import build_report, schema_validation

    schema_result = schema_validation(repo_root)
    if not bool(schema_result.get("valid", False)):
        return {"status": "fail", "message": "universal identity block schema rejected a valid pack identity block"}
    report = build_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "universal identity baseline report did not complete successfully"}
    return {"status": "pass", "message": "universal identity block schema and baseline report are valid"}
