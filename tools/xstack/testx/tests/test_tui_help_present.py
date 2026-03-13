"""FAST test: DIST-5 TUI surface exposes help and required baseline panels."""

from __future__ import annotations


TEST_ID = "test_tui_help_present"
TEST_TAGS = ["fast", "dist", "release", "ux", "tui"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist5_testlib import load_report

    report = load_report(repo_root)
    probe = dict(report.get("tui_probe") or {})
    if not bool(probe.get("show_help")):
        return {"status": "fail", "message": "TUI help is not shown by default"}
    help_lines = [str(item) for item in list(probe.get("help_lines") or [])]
    if not help_lines or "F1 Help" not in help_lines[0]:
        return {"status": "fail", "message": "TUI help header is missing"}
    panel_ids = set(str(item) for item in list(probe.get("panel_ids") or []))
    required = {"panel.menu", "panel.console", "panel.logs", "panel.status"}
    if not required.issubset(panel_ids):
        return {"status": "fail", "message": "TUI required panels are missing"}
    return {"status": "pass", "message": "DIST-5 TUI help and baseline panels are present"}
