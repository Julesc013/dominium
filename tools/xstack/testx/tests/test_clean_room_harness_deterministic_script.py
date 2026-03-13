"""FAST test: DIST-3 clean-room step script ordering is deterministic."""

from __future__ import annotations


TEST_ID = "test_clean_room_harness_deterministic_script"
TEST_TAGS = ["fast", "dist", "release", "determinism"]


def run(repo_root: str):
    del repo_root
    from tools.xstack.testx.tests.dist3_testlib import step_plan

    first = step_plan(seed="456", mode_policy="cli")
    second = step_plan(seed="456", mode_policy="cli")
    if first != second:
        return {"status": "fail", "message": "DIST-3 clean-room step plan drifted across repeated construction"}
    step_ids = [str(row.get("step_id", "")).strip() for row in first]
    expected = [
        "setup_install_status",
        "vpath_probe",
        "setup_verify",
        "launcher_instances_list",
        "launcher_compat_status",
        "launcher_start",
        "launcher_status",
        "launcher_attach_all",
        "teleport_chain",
        "tool_session",
        "diag_capture",
        "replay_verify",
        "launcher_stop",
    ]
    if step_ids != expected:
        return {"status": "fail", "message": "DIST-3 clean-room step ordering no longer matches the documented flow"}
    return {"status": "pass", "message": "DIST-3 clean-room step plan is deterministic"}
