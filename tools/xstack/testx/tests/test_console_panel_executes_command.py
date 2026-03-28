"""FAST test: APPSHELL-3 console panel executes AppShell commands deterministically."""

from __future__ import annotations


TEST_ID = "test_console_panel_executes_command"
TEST_TAGS = ["fast", "appshell", "tui", "console"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell3_testlib import build_surface, ensure_repo_on_path

    ensure_repo_on_path(repo_root)
    from appshell.tui import execute_console_session_command

    surface = build_surface(repo_root, product_id="client", layout_id="layout.viewer", backend_override="lite")
    result = execute_console_session_command(
        repo_root,
        product_id="client",
        mode_id="tui",
        surface_payload=surface,
        command_text="help",
    )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "console execution did not complete"}
    dispatch = dict(result.get("dispatch") or {})
    if str(dispatch.get("dispatch_kind", "")).strip() != "text":
        return {"status": "fail", "message": "help command did not return text dispatch"}
    rebuilt = dict(result.get("surface") or {})
    if str(rebuilt.get("active_panel_id", "")).strip() != "panel.console":
        return {"status": "fail", "message": "console execution did not focus console panel"}
    sessions = list(rebuilt.get("console_sessions") or [])
    if not sessions or not list(dict(sessions[0]).get("history") or []):
        return {"status": "fail", "message": "console session history was not recorded"}
    return {"status": "pass", "message": "console panel executes registered commands deterministically"}
