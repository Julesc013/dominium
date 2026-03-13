"""FAST test: changing source revision input changes build identity."""

from __future__ import annotations


TEST_ID = "test_build_id_changes_on_source_change"
TEST_TAGS = ["fast", "release", "identity"]


def run(repo_root: str):
    del repo_root
    from tools.xstack.testx.tests.release2_testlib import build_id_for_source

    left = build_id_for_source("client", "rev.left")
    right = build_id_for_source("client", "rev.right")
    if left == right:
        return {"status": "fail", "message": "build_id did not change when source revision changed"}
    return {"status": "pass", "message": "build_id changes when source revision input changes"}
