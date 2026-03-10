"""FAST test: rendered UI degrades deterministically to TUI."""

from __future__ import annotations


TEST_ID = "test_rendered_falls_back_to_tui"
TEST_TAGS = ["fast", "compat", "cap_neg", "degrade"]


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg_testlib import build_default_pair, negotiate, runtime_state

    client, server = build_default_pair(repo_root)
    result = negotiate(repo_root, client, server)
    record = dict(result.get("negotiation_record") or {})
    state = runtime_state(repo_root, record)
    if str(state.get("effective_ui_mode", "")) != "tui":
        return {
            "status": "fail",
            "message": "expected rendered fallback to select TUI, got {}".format(str(state.get("effective_ui_mode", ""))),
        }
    return {"status": "pass", "message": "rendered UI falls back to TUI deterministically"}
