"""FAST test: repository inventory output is deterministic across repeated builds."""

from __future__ import annotations


TEST_ID = "test_repo_inventory_deterministic"
TEST_TAGS = ["fast", "review", "inventory", "determinism"]


def run(repo_root: str):
    from tools.xstack.compatx.canonical_json import canonical_json_text
    from tools.xstack.testx.tests.repo_review2_testlib import build_report

    first = build_report(repo_root)
    second = build_report(repo_root)
    if str(first.get("deterministic_fingerprint", "")).strip() != str(second.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "repository inventory fingerprint drifted across repeated builds"}
    if canonical_json_text(first) != canonical_json_text(second):
        return {"status": "fail", "message": "repository inventory canonical JSON drifted across repeated builds"}
    return {"status": "pass", "message": "repository inventory output is deterministic"}
