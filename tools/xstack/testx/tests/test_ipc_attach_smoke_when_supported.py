"""FAST test: products advertising attach-console support pass the IPC smoke lane."""

from __future__ import annotations


TEST_ID = "test_ipc_attach_smoke_when_supported"
TEST_TAGS = ["fast", "mvp", "products", "ipc"]


def run(repo_root: str):
    from tools.xstack.testx.tests.prod_gate0_testlib import ipc_rows, load_report

    report, error = load_report(repo_root, prefer_cached=True)
    if error:
        return {"status": "fail", "message": error}
    rows = ipc_rows(report)
    if not rows:
        return {"status": "fail", "message": "IPC smoke rows are missing for attach-console products"}
    failures = []
    for row in rows:
        row_map = dict(row or {})
        if not bool(row_map.get("passed")):
            failures.append(str(row_map.get("product_id", "")).strip())
            continue
        attach_result = str(row_map.get("attach_result", "")).strip()
        if attach_result not in {"complete", "refused"}:
            failures.append("{} attach_result={}".format(str(row_map.get("product_id", "")).strip(), attach_result or "<missing>"))
    if failures:
        return {"status": "fail", "message": "IPC attach smoke failed for: {}".format(", ".join(sorted(failures)))}
    return {"status": "pass", "message": "attach-console products pass the IPC smoke lane or refuse cleanly"}
