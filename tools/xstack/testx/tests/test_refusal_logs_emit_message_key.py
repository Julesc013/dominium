"""FAST test: refusal paths emit structured log message keys."""

from __future__ import annotations


TEST_ID = "test_refusal_logs_emit_message_key"
TEST_TAGS = ["fast", "appshell", "logging", "refusal"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell0_testlib import run_wrapper
    from tools.xstack.testx.tests.appshell2_testlib import ensure_repo_on_path, load_jsonl

    ensure_repo_on_path(repo_root)
    from appshell.logging import build_default_log_file_path

    report = run_wrapper(repo_root, "dominium_client", ["not-a-command"])
    if int(report.get("returncode", 0)) != 10:
        return {"status": "fail", "message": "refusal command returned unexpected exit code"}
    rows = load_jsonl(build_default_log_file_path(repo_root, "client"))
    if not rows:
        return {"status": "fail", "message": "log file sink did not record refusal events"}
    if "appshell.refusal" not in {str(row.get("message_key", "")).strip() for row in rows}:
        return {"status": "fail", "message": "refusal path did not emit appshell.refusal message key"}
    return {"status": "pass", "message": "refusal logging emits structured message keys"}

