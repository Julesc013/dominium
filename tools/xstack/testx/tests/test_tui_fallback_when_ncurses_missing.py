"""FAST test: APPSHELL-3 falls back deterministically when curses is unavailable."""

from __future__ import annotations


TEST_ID = "test_tui_fallback_when_ncurses_missing"
TEST_TAGS = ["fast", "appshell", "tui", "fallback"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell3_testlib import build_surface

    surface = build_surface(repo_root, product_id="server", layout_id="layout.server", backend_override="lite")
    if str(surface.get("backend_id", "")).strip() != "lite":
        return {"status": "fail", "message": "lite backend override was not honored"}
    if str(surface.get("compatibility_mode_id", "")).strip() != "compat.degraded":
        return {"status": "fail", "message": "lite backend did not record degraded compat mode"}
    if str(surface.get("effective_mode_id", "")).strip() != "cli":
        return {"status": "fail", "message": "lite backend did not degrade to cli mode"}
    disabled = list(surface.get("disabled_capabilities") or [])
    substituted = list(surface.get("substituted_capabilities") or [])
    if not any(str(dict(row).get("capability_id", "")).strip() == "cap.ui.tui" for row in disabled):
        return {"status": "fail", "message": "cap.ui.tui disablement was not recorded"}
    if not any(
        str(dict(row).get("capability_id", "")).strip() == "cap.ui.tui"
        and str(dict(row).get("substitute_capability_id", "")).strip() == "cap.ui.cli"
        for row in substituted
    ):
        return {"status": "fail", "message": "cli substitute was not recorded for tui fallback"}
    return {"status": "pass", "message": "tui fallback is explicit and deterministic"}
