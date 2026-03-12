"""FAST test: unified validation report ordering is deterministic."""

from __future__ import annotations


TEST_ID = "test_validation_report_deterministic_order"
TEST_TAGS = ["fast", "validation", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.validation_unify_testlib import canonical_report_text

    first = canonical_report_text(repo_root, "FAST")
    second = canonical_report_text(repo_root, "FAST")
    if first != second:
        return {"status": "fail", "message": "validation report canonical JSON drifted across repeated builds"}
    return {"status": "pass", "message": "validation report ordering is deterministic"}
