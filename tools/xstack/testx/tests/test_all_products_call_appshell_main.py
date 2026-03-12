"""FAST test: every governed product entrypoint delegates through AppShell."""

from __future__ import annotations


TEST_ID = "test_all_products_call_appshell_main"
TEST_TAGS = ["fast", "appshell", "entrypoint", "convergence"]


def run(repo_root: str):
    from tools.xstack.testx.tests.entrypoint_unify_testlib import build_report, violations

    report = build_report(repo_root)
    bad_rows = [
        row
        for row in list(report.get("rows") or [])
        if not bool(dict(row or {}).get("calls_appshell_main"))
    ]
    if bad_rows:
        first = dict(bad_rows[0] or {})
        return {
            "status": "fail",
            "message": "product '{}' does not call appshell_main".format(str(first.get("product_id", "")).strip()),
        }
    rows = violations(repo_root)
    if rows:
        first = dict(rows[0] or {})
        return {
            "status": "fail",
            "message": "entrypoint unify violation remains: {} {}".format(
                str(first.get("file_path", "")).strip(),
                str(first.get("code", "")).strip(),
            ),
        }
    return {"status": "pass", "message": "all governed product entrypoints delegate through AppShell"}
