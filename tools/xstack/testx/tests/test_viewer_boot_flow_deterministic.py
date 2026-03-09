"""FAST test: UX-0 viewer boot/session flow stays deterministic for the MVP shell."""

from __future__ import annotations

import sys


TEST_ID = "test_viewer_boot_flow_deterministic"
TEST_TAGS = ["fast", "ux", "viewer", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.client.ui.viewer_shell import STATE_BOOT, STATE_BUNDLE_SELECT, STATE_SEED_SELECT, STATE_SESSION_RUNNING
    from src.client.ui.viewer_shell import build_viewer_shell_state

    first = build_viewer_shell_state(
        repo_root=repo_root,
        seed="42",
        authority_mode="dev",
        entrypoint="client",
        ui_mode="gui",
        start_session=True,
    )
    second = build_viewer_shell_state(
        repo_root=repo_root,
        seed="42",
        authority_mode="dev",
        entrypoint="client",
        ui_mode="gui",
        start_session=True,
    )
    if dict(first) != dict(second):
        return {"status": "fail", "message": "UX-0 viewer boot/session state drifted across repeated runs"}
    if str(dict(dict(first.get("state_machine") or {})).get("current_stage", "")).strip() != STATE_SESSION_RUNNING:
        return {"status": "fail", "message": "UX-0 viewer boot flow did not advance to SessionRunning"}
    stage_ids = [str(dict(row).get("stage_id", "")).strip() for row in list(dict(first.get("state_machine") or {}).get("states") or [])]
    if stage_ids != [STATE_BOOT, STATE_BUNDLE_SELECT, STATE_SEED_SELECT, STATE_SESSION_RUNNING]:
        return {"status": "fail", "message": "UX-0 viewer state-machine ordering drifted"}
    if str(dict(dict(first.get("bootstrap") or {}).get("session_spec") or {}).get("universe_seed", "")).strip() != "42":
        return {"status": "fail", "message": "UX-0 viewer boot flow did not retain the requested seed"}
    return {"status": "pass", "message": "UX-0 viewer boot/session flow deterministic for the MVP shell"}
