"""FAST test: PROC-8 replay tool verifies pipeline hash chains."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_replay_pipeline_hash_match"
TEST_TAGS = ["fast", "proc", "proc8", "software", "replay"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.process.tool_replay_pipeline_window import verify_pipeline_replay_window
    from tools.xstack.testx.tests import proc8_testlib

    state = proc8_testlib.cloned_state()
    out = proc8_testlib.execute_pipeline(
        repo_root=repo_root,
        state=state,
        inputs=proc8_testlib.default_inputs(),
    )
    if str(out.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "pipeline execution failed before replay check"}

    first = verify_pipeline_replay_window(state_payload=state)
    if str(first.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "initial pipeline replay verification failed"}

    baseline = copy.deepcopy(state)
    observed = dict(first.get("observed") or {})
    for key in (
        "build_artifact_hash_chain",
        "compiled_model_hash_chain",
        "signature_hash_chain",
        "deployment_hash_chain",
    ):
        baseline[key] = str(observed.get(key, "")).strip()

    second = verify_pipeline_replay_window(
        state_payload=baseline,
        expected_payload=baseline,
    )
    if str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "baseline replay verification failed"}
    return {"status": "pass", "message": "pipeline replay hashes match expected baseline"}
