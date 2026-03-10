"""FAST test: APPSHELL-3 panel ordering is deterministic."""

from __future__ import annotations


TEST_ID = "test_panel_order_deterministic"
TEST_TAGS = ["fast", "appshell", "tui"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell3_testlib import build_surface

    first = build_surface(repo_root, product_id="client", layout_id="layout.viewer", backend_override="lite")
    second = build_surface(repo_root, product_id="client", layout_id="layout.viewer", backend_override="lite")
    if list(first.get("panel_order") or []) != list(second.get("panel_order") or []):
        return {"status": "fail", "message": "panel order drifted across repeated builds"}
    if str(first.get("deterministic_fingerprint", "")).strip() != str(second.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "tui surface fingerprint drifted across repeated builds"}
    return {"status": "pass", "message": "panel ordering is deterministic"}
