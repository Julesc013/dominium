"""FAST test: refusal flows emit structured refusal logs with remediation."""

from __future__ import annotations


TEST_ID = "test_refusals_always_logged"
TEST_TAGS = ["fast", "observability", "refusal"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell0_testlib import run_wrapper
    from tools.xstack.testx.tests.appshell2_testlib import ensure_repo_on_path, load_jsonl

    ensure_repo_on_path(repo_root)
    from appshell.logging import build_default_log_file_path

    report = run_wrapper(repo_root, "dominium_client", ["not-a-command"])
    if int(report.get("returncode", 0)) != 10:
        return {"status": "fail", "message": "refusal command returned unexpected exit code"}
    rows = load_jsonl(build_default_log_file_path(repo_root, "client"))
    refusal_rows = [dict(row) for row in rows if str(dict(row).get("message_key", "")).strip() == "appshell.refusal"]
    if not refusal_rows:
        return {"status": "fail", "message": "refusal path did not emit the guaranteed refusal log"}
    latest = refusal_rows[-1]
    params = dict(latest.get("params") or {})
    if not str(params.get("remediation_hint", "")).strip():
        return {"status": "fail", "message": "refusal log did not include remediation_hint"}
    if not str(params.get("refusal_code", "")).strip():
        return {"status": "fail", "message": "refusal log did not include refusal_code"}
    return {"status": "pass", "message": "refusal flows emit remediation-bearing refusal logs"}
