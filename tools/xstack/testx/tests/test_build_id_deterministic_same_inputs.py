"""FAST test: identical build inputs must produce identical build IDs."""

from __future__ import annotations


TEST_ID = "test_build_id_deterministic_same_inputs"
TEST_TAGS = ["fast", "release", "identity"]


def run(repo_root: str):
    from tools.xstack.testx.tests.release0_testlib import sample_build_metadata

    first = sample_build_metadata(repo_root, "client", source_revision_id="rev.same")
    second = sample_build_metadata(repo_root, "client", source_revision_id="rev.same")
    if str(first.get("build_id", "")) != str(second.get("build_id", "")):
        return {"status": "fail", "message": "build_id drifted for identical inputs"}
    if str(first.get("inputs_hash", "")) != str(second.get("inputs_hash", "")):
        return {"status": "fail", "message": "inputs_hash drifted for identical inputs"}
    return {"status": "pass", "message": "build_id is deterministic for identical inputs"}
