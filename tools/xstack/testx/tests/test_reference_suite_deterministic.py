"""FAST test: META-REF0 reference suite output is deterministic for equal inputs."""

from __future__ import annotations


TEST_ID = "test_reference_suite_deterministic"
TEST_TAGS = ["fast", "meta", "reference", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests import meta_ref0_testlib

    suite_a = meta_ref0_testlib.run_reference_suite_case(
        repo_root=repo_root,
        seed=1731,
        tick_start=0,
        tick_end=3,
    )
    suite_b = meta_ref0_testlib.run_reference_suite_case(
        repo_root=repo_root,
        seed=1731,
        tick_start=0,
        tick_end=3,
    )
    if str(suite_a.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first reference suite returned mismatch/violation"}
    if str(suite_b.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second reference suite returned mismatch/violation"}
    if list(suite_a.get("reference_run_record_rows") or []) != list(suite_b.get("reference_run_record_rows") or []):
        return {"status": "fail", "message": "reference_run_record_rows drifted across equal suite runs"}
    if str(suite_a.get("deterministic_fingerprint", "")).strip() != str(
        suite_b.get("deterministic_fingerprint", "")
    ).strip():
        return {"status": "fail", "message": "reference suite deterministic fingerprint drifted"}
    return {"status": "pass", "message": "reference suite deterministic for equal inputs"}

