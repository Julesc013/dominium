"""FAST test: stable registry entries carry contract ids."""

from __future__ import annotations


TEST_ID = "test_stable_have_contract_id"
TEST_TAGS = ["fast", "meta", "stability", "stable"]


def run(repo_root: str):
    from tools.xstack.testx.tests.stability_classification_testlib import (
        error_codes,
        load_validation_report,
        stability_class_counts,
    )

    report = load_validation_report(repo_root)
    violations = [code for code in error_codes(report) if code == "stable_requires_contract_id"]
    if violations:
        return {"status": "fail", "message": "stable stability markers are missing contract_id"}
    stable_count = int(stability_class_counts(repo_root).get("stable", 0) or 0)
    if stable_count <= 0:
        return {"status": "fail", "message": "expected at least one stable entry in governed registries"}
    return {"status": "pass", "message": "stable entries declare contract_id across all governed registries"}
