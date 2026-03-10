"""FAST test: AppShell refusals map to stable exit codes."""

from __future__ import annotations


TEST_ID = "test_refusal_exit_code_mapping"
TEST_TAGS = ["fast", "appshell", "refusal", "exit_codes"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell1_testlib import load_refusal_to_exit_registry, run_wrapper_json

    report, payload = run_wrapper_json(repo_root, "dominium_client", ["not-a-command"])
    if int(report.get("returncode", 0)) != 10:
        return {"status": "fail", "message": "unknown command exit code drifted from usage range"}
    if str(payload.get("refusal_code", "")).strip() != "refusal.debug.command_unknown":
        return {"status": "fail", "message": "unexpected refusal code for unknown command"}
    if not str(payload.get("remediation_hint", "")).strip():
        return {"status": "fail", "message": "refusal did not include remediation hint"}
    registry = load_refusal_to_exit_registry(repo_root)
    rows = list((dict(registry.get("record") or {})).get("mappings") or [])
    exact = {
        str(dict(row).get("refusal_code", "")).strip(): int(dict(row).get("exit_code", 0) or 0)
        for row in rows
        if isinstance(row, dict) and str(dict(row).get("refusal_code", "")).strip()
    }
    if int(exact.get("refusal.debug.command_unknown", -1)) != 10:
        return {"status": "fail", "message": "refusal-to-exit registry lost exact mapping for unknown command"}
    return {"status": "pass", "message": "refusal exit code mapping remains stable"}
