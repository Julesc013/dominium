"""FAST test: governed registry entry ids remain unique within each file."""

from __future__ import annotations


TEST_ID = "test_no_duplicate_registry_ids"
TEST_TAGS = ["fast", "meta", "stability", "registry"]


def run(repo_root: str):
    from tools.xstack.testx.tests.stability_classification_testlib import duplicate_item_errors, load_validation_report

    report = load_validation_report(repo_root)
    duplicates = duplicate_item_errors(report)
    if duplicates:
        first = duplicates[0]
        return {
            "status": "fail",
            "message": "duplicate registry entry id detected in {} ({})".format(first["file_path"], first["item_id"] or first["path"]),
        }
    return {"status": "pass", "message": "registry entry ids are unique within each governed registry file"}
