"""FAST test: governed truth numeric namespaces are free of unreviewed float usage."""

from __future__ import annotations


TEST_ID = "test_no_float_in_truth_namespace"
TEST_TAGS = ["fast", "numeric", "governance"]


def run(repo_root: str):
    from tools.xstack.testx.tests.numeric_discipline_testlib import float_in_truth_blocking_count

    blocking = float_in_truth_blocking_count(repo_root)
    if blocking:
        return {"status": "fail", "message": "numeric truth scan found {} blocking float findings".format(blocking)}
    return {"status": "pass", "message": "numeric truth scan found no blocking float findings"}
