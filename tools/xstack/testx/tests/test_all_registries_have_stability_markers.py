"""FAST test: scoped META-STABILITY-0 registries carry stability markers."""

from __future__ import annotations


TEST_ID = "test_all_registries_have_stability_markers"
TEST_TAGS = ["fast", "meta", "stability", "registry"]


def run(repo_root: str):
    from tools.xstack.testx.tests.stability_classification_testlib import error_codes, load_validation_report

    report = load_validation_report(repo_root)
    missing = [code for code in error_codes(report) if code == "missing_stability"]
    if missing:
        return {"status": "fail", "message": "scoped registry entries are missing stability markers"}
    return {"status": "pass", "message": "all populated scoped registries carry stability markers"}

