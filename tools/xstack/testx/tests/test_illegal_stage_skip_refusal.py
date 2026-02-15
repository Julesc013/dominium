"""STRICT test: illegal pipeline stage skips refuse deterministically."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.session.illegal_stage_skip_refusal"
TEST_TAGS = ["strict", "session"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.pipeline_contract import load_session_pipeline_contract
    from tools.xstack.sessionx.runner import _simulate_boot_stage_log

    contract = load_session_pipeline_contract(repo_root=repo_root, pipeline_id="pipeline.client.default")
    if contract.get("result") != "complete":
        return {"status": "fail", "message": "unable to load pipeline contract for stage skip refusal test"}

    tampered = copy.deepcopy(contract)
    tampered["stage_order"] = [
        "stage.resolve_session",
        "stage.verify_world",
        "stage.session_ready",
    ]
    stage_log, last_stage, err = _simulate_boot_stage_log(
        pipeline_contract=tampered,
        authority_context={"privilege_level": "observer"},
        simulation_tick=0,
    )
    if stage_log or last_stage:
        return {"status": "fail", "message": "illegal skip should not produce stage log output"}
    if not isinstance(err, dict) or err.get("result") != "refused":
        return {"status": "fail", "message": "illegal stage skip should refuse"}

    refusal = dict(err.get("refusal") or {})
    if str(refusal.get("reason_code", "")) != "refusal.stage_invalid_transition":
        return {
            "status": "fail",
            "message": "expected refusal.stage_invalid_transition, got '{}'".format(str(refusal.get("reason_code", ""))),
        }
    return {"status": "pass", "message": "illegal stage skip refusal checks passed"}
