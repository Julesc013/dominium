"""FAST test: changing deterministic build inputs must change build identity."""

from __future__ import annotations


TEST_ID = "test_build_id_changes_when_inputs_change"
TEST_TAGS = ["fast", "release", "identity"]


def run(repo_root: str):
    from tools.xstack.testx.tests.release0_testlib import sample_build_metadata

    left = sample_build_metadata(repo_root, "client", source_revision_id="rev.left")
    right = sample_build_metadata(repo_root, "client", source_revision_id="rev.right")
    if str(left.get("build_id", "")) == str(right.get("build_id", "")):
        return {"status": "fail", "message": "build_id did not change when source revision input changed"}
    return {"status": "pass", "message": "build_id changes when deterministic inputs change"}
