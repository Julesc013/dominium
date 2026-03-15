"""FAST test: derived parallel output is canonicalized before hashing or persistence."""

from __future__ import annotations


TEST_ID = "test_derived_parallel_output_canonicalized"
TEST_TAGS = ["fast", "concurrency", "derived", "determinism"]


def run(repo_root: str):
    del repo_root
    from tools.xstack.testx.tests.concurrency_contract_testlib import build_derived_rows

    rows = build_derived_rows()
    artifact_ids = [str(dict(row).get("artifact_id", "")).strip() for row in rows]
    if artifact_ids != ["artifact.a", "artifact.b", "artifact.d", "artifact.c"]:
        return {"status": "fail", "message": "derived parallel rows were not canonicalized by tile/sub-index ordering"}
    return {"status": "pass", "message": "derived parallel output canonicalization passed"}
