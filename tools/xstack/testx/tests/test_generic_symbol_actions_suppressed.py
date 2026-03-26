"""FAST test: generic helper symbols do not produce secondary convergence actions."""

from __future__ import annotations


TEST_ID = "test_generic_symbol_actions_suppressed"
TEST_TAGS = ["fast", "xi", "convergence", "generic"]


def run(repo_root: str):
    from tools.xstack.testx.tests.convergence_plan_testlib import committed_convergence_actions

    payload = committed_convergence_actions(repo_root)
    actions = list(payload.get("actions") or [])
    blocked_symbols = {"main", "report_json_path", "_read_text", "_write_json", "run"}
    offenders = [
        dict(row)
        for row in actions
        if str(dict(row).get("symbol_name", "")).strip() in blocked_symbols
        and str(dict(row).get("kind", "")).strip() != "keep"
    ]
    if offenders:
        sample = offenders[0]
        return {
            "status": "fail",
            "message": "generic helper symbols must not produce secondary convergence actions: "
            f"{sample.get('symbol_name')} -> {sample.get('kind')}",
        }
    return {"status": "pass", "message": "generic helper symbols are suppressed from secondary convergence actions"}
