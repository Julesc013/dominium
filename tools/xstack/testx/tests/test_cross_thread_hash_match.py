"""FAST test: MVP stress cross-thread hashes match."""

from __future__ import annotations


TEST_ID = "test_cross_thread_hash_match"
TEST_TAGS = ["fast", "mvp", "stress", "threads"]


def run(repo_root: str):
    from tools.xstack.testx.tests.mvp_stress_testlib import load_report

    report, error = load_report(repo_root)
    if error:
        return {"status": "fail", "message": error}
    if not bool(dict(report.get("assertions") or {}).get("cross_thread_hash_match", False)):
        return {"status": "fail", "message": "MVP stress report did not record cross_thread_hash_match=true"}
    cross_thread_checks = dict(report.get("cross_thread_checks") or {})
    for suite_id, row in sorted(cross_thread_checks.items(), key=lambda item: str(item[0])):
        hashes_value = dict(row or {}).get("hashes")
        hashes = dict(hashes_value) if isinstance(hashes_value, dict) else {}
        if not hashes:
            values = [str(item).strip() for item in list(hashes_value or []) if str(item).strip()] if isinstance(hashes_value, list) else []
            if not values:
                continue
            hashes = {str(index + 1): value for index, value in enumerate(values)}
        if len(set(hashes.values())) > 1:
            return {"status": "fail", "message": "MVP stress cross-thread hash mismatch for {}".format(suite_id)}
    return {"status": "pass", "message": "MVP stress cross-thread hashes match"}
