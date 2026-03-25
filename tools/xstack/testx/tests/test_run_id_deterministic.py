"""FAST test: Ω-9 run ids remain deterministic for identical env/profile/source inputs."""

from __future__ import annotations


TEST_ID = "test_run_id_deterministic"
TEST_TAGS = ["fast", "omega", "toolchain", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.toolchain_matrix_testlib import deterministic_run_id

    left_run_id, left_payload = deterministic_run_id(repo_root)
    right_run_id, right_payload = deterministic_run_id(repo_root)
    if left_run_id != right_run_id:
        return {"status": "fail", "message": "toolchain run_id drifted across identical inputs"}
    if left_payload != right_payload:
        return {"status": "fail", "message": "toolchain run input payload drifted across identical inputs"}
    return {"status": "pass", "message": "toolchain run_id is deterministic"}
