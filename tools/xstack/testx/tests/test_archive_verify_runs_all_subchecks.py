"""STRICT test: offline archive verification executes and passes the full Ω subcheck set."""

from __future__ import annotations


TEST_ID = "test_archive_verify_runs_all_subchecks"
TEST_TAGS = ["strict", "omega", "archive", "verification"]


def run(repo_root: str):
    from tools.xstack.testx.tests.offline_archive_testlib import build_and_verify, required_subcheck_ids

    _build_report, verify_report = build_and_verify(repo_root, "shared")
    if str(verify_report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "offline archive verification did not pass"}
    subchecks = dict(verify_report.get("subchecks") or {})
    for check_id in required_subcheck_ids():
        if str(dict(subchecks.get(check_id) or {}).get("result", "")).strip() != "complete":
            return {"status": "fail", "message": "offline archive subcheck '{}' did not pass".format(check_id)}
    return {"status": "pass", "message": "offline archive verification passes the full Ω subcheck set"}
