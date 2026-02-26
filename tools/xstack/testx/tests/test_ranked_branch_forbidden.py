"""STRICT test: ranked time policy forbids branching."""

from __future__ import annotations

import sys


TEST_ID = "testx.time.ranked_branch_forbidden"
TEST_TAGS = ["strict", "time", "branching", "ranked"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.time_lineage import branch_from_checkpoint
    from tools.xstack.testx.tests.time_rs3_testlib import (
        camera_move_intents,
        checkpoint_id_from_run_result,
        create_session,
        run_script,
        write_script,
    )

    save_id = "save.testx.time.rank_branch_forbidden"
    fixture, created = create_session(
        repo_root=repo_root,
        save_id=save_id,
        time_control_policy_id="time.policy.rank_strict",
        physics_profile_id="physics.default.realistic",
    )
    if str(created.get("result", "")) != "complete":
        return {"status": "fail", "message": "session create failed before ranked branching refusal test"}

    script_abs = write_script(
        repo_root=repo_root,
        save_id=save_id,
        script_id="ranked.branch.refusal",
        intents=camera_move_intents(10, prefix="ranked.branch"),
    )
    run_result = run_script(
        repo_root=repo_root,
        created=created,
        fixture=fixture,
        script_abs=script_abs,
        write_state=False,
    )
    if str(run_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "script run failed before ranked branch refusal check"}
    checkpoint_id = checkpoint_id_from_run_result(repo_root, run_result)
    if not checkpoint_id:
        return {"status": "fail", "message": "expected ranked save to produce checkpoint before branch refusal check"}

    branch_result = branch_from_checkpoint(
        repo_root=repo_root,
        parent_checkpoint_id=checkpoint_id,
        new_save_id="save.testx.time.rank_branch_forbidden.child",
        reason="testx.ranked_branch_forbidden",
        parent_save_id=save_id,
    )
    if str(branch_result.get("result", "")) == "complete":
        return {"status": "fail", "message": "ranked time policy unexpectedly allowed branch creation"}
    reason_code = str((branch_result.get("refusal") or {}).get("reason_code", ""))
    if reason_code != "refusal.time.branch_forbidden_by_policy":
        return {"status": "fail", "message": "unexpected refusal code '{}'".format(reason_code)}
    return {"status": "pass", "message": "ranked time policy deterministically refuses branching"}
