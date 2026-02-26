"""STRICT test: branching from checkpoint creates a replayable new lineage."""

from __future__ import annotations

import os
import shutil
import sys


TEST_ID = "testx.time.branching_creates_new_lineage"
TEST_TAGS = ["strict", "time", "branching"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.time_lineage import branch_from_checkpoint
    from tools.xstack.testx.tests.time_rs3_testlib import (
        camera_move_intents,
        checkpoint_id_from_run_result,
        create_session,
        load_json,
        run_script,
        run_script_with_session_spec,
        write_script,
    )

    parent_save_id = "save.testx.time.branch_parent"
    child_save_id = "save.testx.time.branch_child"
    child_save_abs = os.path.join(repo_root, "saves", child_save_id.replace("/", os.sep))
    if os.path.isdir(child_save_abs):
        shutil.rmtree(child_save_abs, ignore_errors=True)

    fixture, created = create_session(
        repo_root=repo_root,
        save_id=parent_save_id,
        time_control_policy_id="time.policy.default_realistic",
        physics_profile_id="physics.default.realistic",
    )
    if str(created.get("result", "")) != "complete":
        return {"status": "fail", "message": "session create failed before branching test"}

    parent_script_abs = write_script(
        repo_root=repo_root,
        save_id=parent_save_id,
        script_id="branch.parent",
        intents=camera_move_intents(20, prefix="branch.parent"),
    )
    parent_run = run_script(
        repo_root=repo_root,
        created=created,
        fixture=fixture,
        script_abs=parent_script_abs,
        write_state=False,
    )
    if str(parent_run.get("result", "")) != "complete":
        return {"status": "fail", "message": "parent run failed before branch operation"}
    checkpoint_id = checkpoint_id_from_run_result(repo_root, parent_run)
    if not checkpoint_id:
        return {"status": "fail", "message": "branch test expected at least one checkpoint artifact"}

    branch_result = branch_from_checkpoint(
        repo_root=repo_root,
        parent_checkpoint_id=checkpoint_id,
        new_save_id=child_save_id,
        reason="testx.branching.creates_new_lineage",
        parent_save_id=parent_save_id,
    )
    if str(branch_result.get("result", "")) != "complete":
        reason_code = str((branch_result.get("refusal") or {}).get("reason_code", ""))
        return {"status": "fail", "message": "branch creation failed: {}".format(reason_code or "unknown refusal")}

    parent_branch_rel = str(branch_result.get("parent_branch_artifact_path", ""))
    child_branch_rel = str(branch_result.get("new_branch_artifact_path", ""))
    if not parent_branch_rel or not child_branch_rel:
        return {"status": "fail", "message": "branch result missing parent/child branch artifact paths"}
    if not os.path.isfile(os.path.join(repo_root, parent_branch_rel.replace("/", os.sep))):
        return {"status": "fail", "message": "parent branch artifact path was not created"}
    if not os.path.isfile(os.path.join(repo_root, child_branch_rel.replace("/", os.sep))):
        return {"status": "fail", "message": "child branch artifact path was not created"}

    branch_payload = load_json(repo_root, parent_branch_rel)
    if str(branch_payload.get("new_save_id", "")) != child_save_id:
        return {"status": "fail", "message": "branch artifact new_save_id mismatch"}
    if str(branch_payload.get("parent_save_id", "")) != parent_save_id:
        return {"status": "fail", "message": "branch artifact parent_save_id mismatch"}

    child_script_abs = write_script(
        repo_root=repo_root,
        save_id=child_save_id,
        script_id="branch.child.replay",
        intents=camera_move_intents(3, prefix="branch.child"),
    )
    child_run = run_script_with_session_spec(
        repo_root=repo_root,
        session_spec_path=str(branch_result.get("new_session_spec_path", "")),
        bundle_id=str(fixture.get("bundle_id", "bundle.base.lab")),
        script_abs=child_script_abs,
        write_state=False,
    )
    if str(child_run.get("result", "")) != "complete":
        return {"status": "fail", "message": "branched save could not replay intents deterministically"}
    if str(child_run.get("save_id", "")) != child_save_id:
        return {"status": "fail", "message": "branched replay did not execute against new save lineage"}
    return {"status": "pass", "message": "branching produced new lineage artifacts and replayable child save"}
