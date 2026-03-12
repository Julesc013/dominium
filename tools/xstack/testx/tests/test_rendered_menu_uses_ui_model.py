"""FAST test: the rendered menu surface binds through the shared UI model."""

from __future__ import annotations


TEST_ID = "test_rendered_menu_uses_ui_model"
TEST_TAGS = ["fast", "ui", "rendered"]


def run(repo_root: str):
    from tools.xstack.testx.tests.ui_reconcile_testlib import build_client_menu_surface, ensure_repo_on_path

    ensure_repo_on_path(repo_root)
    from src.ui import MENU_STATE_MAIN, build_ui_model

    surface = build_client_menu_surface(repo_root, current_state_id=MENU_STATE_MAIN, seed_value="456")
    model = build_ui_model(repo_root=repo_root, product_id="client", current_state_id=MENU_STATE_MAIN, seed_value="456")
    if str(dict(surface.get("ui_contract") or {}).get("shared_ui_model", "")).strip() != "src/ui/ui_model.py":
        return {"status": "fail", "message": "rendered menu surface does not declare the shared UI model"}
    if str(surface.get("ui_model_fingerprint", "")).strip() != str(model.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "rendered menu surface fingerprint does not match the shared UI model"}
    if str(surface.get("deterministic_fingerprint", "")).strip() == "":
        return {"status": "fail", "message": "rendered menu surface missing deterministic_fingerprint"}
    return {"status": "pass", "message": "rendered menu surface is derived from the shared UI model"}

