"""FAST test: explicit mode overrides remain authoritative with deterministic fallback."""

from __future__ import annotations


TEST_ID = "test_mode_selection_respects_override"
TEST_TAGS = ["fast", "appshell", "platform", "mode_selection"]


def run(repo_root: str):
    from tools.xstack.testx.tests.ui_mode_resolution_testlib import probe, selection

    payload = selection(
        repo_root,
        product_id="client",
        requested_mode_id="cli",
        mode_source="explicit",
        mode_requested=True,
        probe_payload=probe(
            repo_root,
            product_id="client",
            tty=False,
            gui=True,
            native=False,
            rendered=True,
            tui=True,
        ),
    )
    if str(payload.get("selected_mode_id", "")).strip() != "cli":
        return {"status": "fail", "message": "explicit cli override was not honored"}
    if list(payload.get("degrade_chain") or []):
        return {"status": "fail", "message": "explicit cli override should not degrade when cli is available"}
    return {"status": "pass", "message": "explicit mode overrides remain authoritative"}
