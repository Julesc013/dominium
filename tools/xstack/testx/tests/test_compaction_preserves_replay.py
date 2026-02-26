"""STRICT test: deterministic compaction preserves replay outputs."""

from __future__ import annotations

import sys


TEST_ID = "testx.time.compaction_preserves_replay"
TEST_TAGS = ["strict", "time", "compaction", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.time_lineage import compact_save
    from tools.xstack.testx.tests.time_rs3_testlib import camera_move_intents, create_session, run_script, write_script

    save_id = "save.testx.time.compaction_preserves_replay"
    fixture, created = create_session(
        repo_root=repo_root,
        save_id=save_id,
        time_control_policy_id="time.policy.default_realistic",
        physics_profile_id="physics.default.realistic",
    )
    if str(created.get("result", "")) != "complete":
        return {"status": "fail", "message": "session create failed before compaction replay test"}

    script_abs = write_script(
        repo_root=repo_root,
        save_id=save_id,
        script_id="compaction.replay",
        intents=camera_move_intents(40, prefix="compact"),
    )
    baseline = run_script(
        repo_root=repo_root,
        created=created,
        fixture=fixture,
        script_abs=script_abs,
        write_state=False,
    )
    if str(baseline.get("result", "")) != "complete":
        return {"status": "fail", "message": "baseline run failed before compaction"}

    compact_result = compact_save(
        repo_root=repo_root,
        save_id=save_id,
        compaction_policy_id="compaction.policy.default",
    )
    if str(compact_result.get("result", "")) != "complete":
        reason_code = str((compact_result.get("refusal") or {}).get("reason_code", ""))
        return {"status": "fail", "message": "compaction failed: {}".format(reason_code or "unknown refusal")}
    if not bool(compact_result.get("retained_hashes_unchanged", False)):
        return {"status": "fail", "message": "compaction changed hash of retained canonical artifacts"}

    replay = run_script(
        repo_root=repo_root,
        created=created,
        fixture=fixture,
        script_abs=script_abs,
        write_state=False,
    )
    if str(replay.get("result", "")) != "complete":
        return {"status": "fail", "message": "replay after compaction failed"}

    keys = (
        "deterministic_fields_hash",
        "final_state_hash",
        "composite_hash",
        "perceived_model_hash",
        "render_model_hash",
    )
    for key in keys:
        if str(baseline.get(key, "")) != str(replay.get(key, "")):
            return {"status": "fail", "message": "post-compaction replay mismatch for '{}'".format(key)}
    if list(baseline.get("state_hash_anchors") or []) != list(replay.get("state_hash_anchors") or []):
        return {"status": "fail", "message": "state hash anchors changed after compaction replay"}
    if list(baseline.get("tick_hash_anchors") or []) != list(replay.get("tick_hash_anchors") or []):
        return {"status": "fail", "message": "tick hash anchors changed after compaction replay"}
    return {"status": "pass", "message": "deterministic compaction preserves replay outputs"}
