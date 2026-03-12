"""FAST test: superseded or contradictory docs link to a replacement document."""

from __future__ import annotations


TEST_ID = "test_superseded_docs_have_replacement_link"
TEST_TAGS = ["fast", "review", "docs", "supersession"]


def run(repo_root: str):
    from tools.xstack.testx.tests.repo_review3_testlib import superseded_without_replacement

    rows = superseded_without_replacement(repo_root)
    if rows:
        first = dict(rows[0] or {})
        return {
            "status": "fail",
            "message": "superseded doc missing replacement link detected in {} ({})".format(
                str(first.get("path", "")).strip() or "<unknown>",
                str(first.get("alignment_status", "")).strip() or "<unknown>",
            ),
        }
    return {"status": "pass", "message": "superseded and contradictory docs declare replacement links"}
