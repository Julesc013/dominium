"""FAST test: log event ids increase monotonically within a process run."""

from __future__ import annotations


TEST_ID = "test_log_event_ids_monotonic"
TEST_TAGS = ["fast", "appshell", "logging"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell2_testlib import ensure_repo_on_path

    ensure_repo_on_path(repo_root)
    from src.appshell.logging import create_log_engine

    engine = create_log_engine(product_id="client", build_id="build.test", console_enabled=False)
    rows = [
        engine.emit(category="appshell", severity="info", message_key="appshell.bootstrap.start"),
        engine.emit(category="appshell", severity="info", message_key="appshell.command.dispatch"),
        engine.emit(category="diag", severity="info", message_key="diag.snapshot.written"),
    ]
    event_ids = [str(row.get("event_id", "")).strip() for row in rows]
    if event_ids != sorted(event_ids):
        return {"status": "fail", "message": "event ids are not monotonic"}
    if len(set(event_ids)) != len(event_ids):
        return {"status": "fail", "message": "event ids are not unique"}
    return {"status": "pass", "message": "event ids remain monotonic within the process run"}

