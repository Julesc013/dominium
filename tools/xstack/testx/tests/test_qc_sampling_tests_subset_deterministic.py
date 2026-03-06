"""FAST test: PROC-8 deterministic test-subset sampling is stable."""

from __future__ import annotations

import sys


TEST_ID = "test_qc_sampling_tests_subset_deterministic"
TEST_TAGS = ["fast", "proc", "proc8", "software", "qc"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests import proc8_testlib

    inputs = proc8_testlib.default_inputs()
    inputs["test_subset_rate_permille"] = 350
    inputs["available_test_ids"] = [
        "test.alpha",
        "test.beta",
        "test.gamma",
        "test.delta",
        "test.epsilon",
    ]

    state_a = proc8_testlib.cloned_state()
    state_b = proc8_testlib.cloned_state()
    out_a = proc8_testlib.execute_pipeline(repo_root=repo_root, state=state_a, inputs=inputs)
    out_b = proc8_testlib.execute_pipeline(repo_root=repo_root, state=state_b, inputs=inputs)
    if str(out_a.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first deterministic subset execution failed"}
    if str(out_b.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second deterministic subset execution failed"}

    selected_a = list(out_a.get("selected_tests") or [])
    selected_b = list(out_b.get("selected_tests") or [])
    if selected_a != selected_b:
        return {"status": "fail", "message": "deterministic test subset mismatch"}
    if not selected_a:
        return {"status": "fail", "message": "deterministic test subset unexpectedly empty"}
    if len(selected_a) > len(list(inputs.get("available_test_ids") or [])):
        return {"status": "fail", "message": "selected deterministic test subset exceeds candidates"}
    return {"status": "pass", "message": "deterministic QC test subset is stable"}
