"""FAST test: the shared UI model drives menu states through commands and selection events."""

from __future__ import annotations


TEST_ID = "test_ui_model_drives_main_menu_flow_via_commands"
TEST_TAGS = ["fast", "ui", "appshell"]


def run(repo_root: str):
    from tools.xstack.testx.tests.ui_reconcile_testlib import ensure_repo_on_path

    ensure_repo_on_path(repo_root)
    from ui import MENU_STATE_MAIN, MENU_STATE_START_SESSION, build_ui_model

    main_model = build_ui_model(repo_root=repo_root, product_id="client", current_state_id=MENU_STATE_MAIN, seed_value="456")
    start_model = build_ui_model(
        repo_root=repo_root,
        product_id="client",
        current_state_id=MENU_STATE_START_SESSION,
        seed_value="456",
    )
    main_state = dict(main_model.get("current_state") or {})
    start_state = dict(start_model.get("current_state") or {})
    if str(main_model.get("current_state_id", "")).strip() != MENU_STATE_MAIN:
        return {"status": "fail", "message": "shared UI model did not resolve the main menu state deterministically"}
    if str(start_model.get("current_state_id", "")).strip() != MENU_STATE_START_SESSION:
        return {"status": "fail", "message": "shared UI model did not resolve the start-session state deterministically"}
    action_kinds = {str(dict(row).get("action_kind", "")).strip() for row in list(main_state.get("actions") or [])}
    if not {"command", "selection_event"}.intersection(action_kinds):
        return {"status": "fail", "message": "main menu state did not expose command or selection actions"}
    start_actions = [dict(row) for row in list(start_state.get("actions") or [])]
    if not start_actions:
        return {"status": "fail", "message": "start-session state did not expose launch actions"}
    if str(main_model.get("deterministic_fingerprint", "")).strip() == str(start_model.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "distinct menu states collapsed to the same deterministic surface"}
    return {"status": "pass", "message": "shared UI model drives deterministic menu states and actions"}

