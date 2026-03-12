"""FAST test: repository inventory contains no unknown layer classifications."""

from __future__ import annotations


TEST_ID = "test_module_classification_has_no_unknown_entries"
TEST_TAGS = ["fast", "review", "inventory", "classification"]


def run(repo_root: str):
    from tools.xstack.testx.tests.repo_review2_testlib import unknown_entries

    rows = unknown_entries(repo_root)
    if rows:
        first = dict(rows[0] or {})
        return {
            "status": "fail",
            "message": "repository inventory left unknown layer entry '{}'".format(str(first.get("path", "")).strip()),
        }
    return {"status": "pass", "message": "repository inventory classified every scanned module"}
