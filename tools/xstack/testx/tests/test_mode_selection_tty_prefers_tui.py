"""FAST test: TTY contexts prefer TUI before CLI for interactive products."""

from __future__ import annotations


TEST_ID = "test_mode_selection_tty_prefers_tui"
TEST_TAGS = ["fast", "appshell", "platform", "mode_selection"]


def run(repo_root: str):
    from tools.xstack.testx.tests.ui_mode_resolution_testlib import probe, selection

    payload = selection(
        repo_root,
        product_id="launcher",
        probe_payload=probe(
            repo_root,
            product_id="launcher",
            tty=True,
            gui=True,
            native=False,
            rendered=False,
            tui=True,
        ),
    )
    if str(payload.get("selected_mode_id", "")).strip() != "tui":
        return {"status": "fail", "message": "TTY launcher context did not prefer tui"}
    if str(payload.get("context_kind", "")).strip() != "tty":
        return {"status": "fail", "message": "TTY launcher context was not classified as tty"}
    return {"status": "pass", "message": "TTY contexts prefer TUI deterministically"}
