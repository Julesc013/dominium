"""FAST test: provisional registry entries carry replacement metadata."""

from __future__ import annotations


TEST_ID = "test_provisional_have_replacement"
TEST_TAGS = ["fast", "meta", "stability", "provisional"]


def run(repo_root: str):
    from tools.xstack.testx.tests.stability_classification_testlib import (
        error_codes,
        load_validation_report,
        stability_class_counts,
    )

    report = load_validation_report(repo_root)
    violations = [
        code
        for code in error_codes(report)
        if code in ("provisional_requires_future_series", "provisional_requires_replacement_target")
    ]
    if violations:
        return {"status": "fail", "message": "provisional stability markers are missing replacement metadata"}
    provisional_count = int(stability_class_counts(repo_root).get("provisional", 0) or 0)
    if provisional_count <= 0:
        return {"status": "fail", "message": "expected at least one provisional entry in governed registries"}
    return {"status": "pass", "message": "provisional entries declare future_series and replacement_target"}
