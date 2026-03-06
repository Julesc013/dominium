"""FAST test: PROC-8 deploy requires signing key/signature."""

from __future__ import annotations

import sys


TEST_ID = "test_signature_required_for_deploy"
TEST_TAGS = ["fast", "proc", "proc8", "software", "signing"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests import proc8_testlib

    state = proc8_testlib.cloned_state()
    inputs = proc8_testlib.default_inputs()
    inputs["signing_key_artifact_id"] = ""
    inputs["deploy_to_address"] = "sig://station.require.signature"

    result = proc8_testlib.execute_pipeline(repo_root=repo_root, state=state, inputs=inputs)
    if str(result.get("result", "")).strip() != "refused":
        return {"status": "fail", "message": "deploy without signing key should be refused"}

    refusal = dict(result.get("refusal") or {})
    reason = str(refusal.get("reason_code", "")).strip()
    if reason != "refusal.software_pipeline.signing_key_required":
        return {"status": "fail", "message": "unexpected refusal reason for unsigned deploy"}
    return {"status": "pass", "message": "unsigned deploy is correctly refused"}
