"""FAST test: GUI contexts prefer OS-native mode when policy and adapters allow it."""

from __future__ import annotations


TEST_ID = "test_mode_selection_gui_prefers_native_when_available"
TEST_TAGS = ["fast", "appshell", "platform", "mode_selection"]


def run(repo_root: str):
    from tools.xstack.testx.tests.ui_mode_resolution_testlib import probe, selection

    payload = selection(
        repo_root,
        product_id="setup",
        probe_payload=probe(
            repo_root,
            product_id="setup",
            tty=False,
            gui=True,
            native=True,
            rendered=False,
            tui=True,
        ),
    )
    if str(payload.get("selected_mode_id", "")).strip() != "os_native":
        return {"status": "fail", "message": "GUI setup context did not prefer os_native when available"}
    if str(payload.get("context_kind", "")).strip() != "gui":
        return {"status": "fail", "message": "GUI setup context was not classified as gui"}
    return {"status": "pass", "message": "GUI contexts prefer OS-native mode when available"}
