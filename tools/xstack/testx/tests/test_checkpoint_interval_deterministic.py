"""STRICT test: checkpoint interval scheduling is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.time.checkpoint_interval_deterministic"
TEST_TAGS = ["strict", "time", "checkpoint", "determinism"]


def _ticks_from_checkpoint_payloads(rows: list[dict]) -> list[int]:
    return [int((dict(row).get("tick", 0) or 0)) for row in rows]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.time_rs3_testlib import (
        camera_move_intents,
        checkpoint_payloads_from_run_result,
        create_session,
        run_script,
        write_script,
    )

    save_id = "save.testx.time.checkpoint_interval"
    fixture, created = create_session(
        repo_root=repo_root,
        save_id=save_id,
        time_control_policy_id="time.policy.default_realistic",
        physics_profile_id="physics.default.realistic",
    )
    if str(created.get("result", "")) != "complete":
        return {"status": "fail", "message": "session create failed before checkpoint interval test"}

    script_abs = write_script(
        repo_root=repo_root,
        save_id=save_id,
        script_id="checkpoint.interval",
        intents=camera_move_intents(33, prefix="ckpt"),
    )
    first = run_script(
        repo_root=repo_root,
        created=created,
        fixture=fixture,
        script_abs=script_abs,
        write_state=False,
    )
    second = run_script(
        repo_root=repo_root,
        created=created,
        fixture=fixture,
        script_abs=script_abs,
        write_state=False,
    )
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "script run failed before deterministic checkpoint interval comparison"}

    first_paths = list(first.get("checkpoint_artifact_paths") or [])
    second_paths = list(second.get("checkpoint_artifact_paths") or [])
    if first_paths != second_paths:
        return {"status": "fail", "message": "checkpoint artifact path order changed across identical runs"}

    first_payloads = checkpoint_payloads_from_run_result(repo_root, first)
    second_payloads = checkpoint_payloads_from_run_result(repo_root, second)
    first_ticks = _ticks_from_checkpoint_payloads(first_payloads)
    second_ticks = _ticks_from_checkpoint_payloads(second_payloads)
    if first_ticks != second_ticks:
        return {"status": "fail", "message": "checkpoint tick schedule diverged across identical runs"}

    expected_ticks = [16, 32]
    if first_ticks != expected_ticks:
        return {
            "status": "fail",
            "message": "unexpected checkpoint ticks {}; expected {}".format(first_ticks, expected_ticks),
        }
    return {"status": "pass", "message": "checkpoint interval scheduling is deterministic at policy cadence"}
