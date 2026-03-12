"""FAST test: all governed documentation entries declare stability metadata."""

from __future__ import annotations


TEST_ID = "test_all_docs_have_stability_header"
TEST_TAGS = ["fast", "review", "docs", "stability"]


def run(repo_root: str):
    from tools.xstack.testx.tests.repo_review3_testlib import missing_stability_headers

    rows = missing_stability_headers(repo_root)
    if rows:
        first = dict(rows[0] or {})
        return {
            "status": "fail",
            "message": "doc missing stability header detected in {} ({})".format(
                str(first.get("path", "")).strip() or "<unknown>",
                str(first.get("alignment_status", "")).strip() or "<unknown>",
            ),
        }
    return {"status": "pass", "message": "all governed documentation entries declare stability metadata"}
