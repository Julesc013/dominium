"""FAST test: AppShell IPC uses a single canonical transport surface."""

from __future__ import annotations


TEST_ID = "test_single_ipc_transport_used"
TEST_TAGS = ["fast", "appshell", "ipc", "transport"]


def run(repo_root: str):
    from tools.xstack.testx.tests.ipc_unify_testlib import build_report

    report = build_report(repo_root, include_runtime=False)
    violations = list(report.get("violations") or [])
    if violations:
        return {"status": "fail", "message": "IPC unify report has static violations"}
    rows = list(report.get("direct_socket_users") or [])
    runtime_rows = [dict(row) for row in rows if str(dict(row).get("classification", "")).strip() == "canonical"]
    paths = sorted(str(dict(row).get("path", "")).strip() for row in runtime_rows if str(dict(row).get("path", "")).strip())
    if paths != ["appshell/ipc/ipc_transport.py"]:
        return {"status": "fail", "message": "unexpected direct socket surface set: {}".format(", ".join(paths) or "<none>")}
    return {"status": "pass", "message": "direct socket usage is confined to the canonical IPC transport"}
