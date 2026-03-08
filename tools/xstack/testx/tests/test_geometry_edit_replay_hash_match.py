"""FAST test: GEO-10 geometry edit replay matches stress proof surfaces across suites."""

from __future__ import annotations


TEST_ID = "test_geometry_edit_replay_hash_match"
TEST_TAGS = ["fast", "geo", "geometry", "stress"]


def run(repo_root: str):
    from tools.xstack.testx.tests.geo10_testlib import geo10_replay_report, geo10_stress_report

    stress_report = geo10_stress_report(repo_root)
    replay_report = geo10_replay_report(repo_root)
    if str(stress_report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "GEO-10 stress report did not complete"}
    if str(replay_report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "GEO-10 replay report did not complete"}
    replay_rows = {
        str(dict(row).get("suite_id", "")).strip(): dict(row)
        for row in list(dict(replay_report.get("observed") or {}).get("suite_snapshots") or [])
    }
    for row in list(stress_report.get("topology_suite_reports") or []):
        suite_id = str(dict(row).get("suite_id", "")).strip()
        proof_summary = dict(dict(row).get("proof_summary") or {})
        replay_row = dict(replay_rows.get(suite_id) or {})
        if str(proof_summary.get("geometry_state_hash_chain", "")).strip() != str(replay_row.get("geometry_state_hash_chain", "")).strip():
            return {"status": "fail", "message": "geometry state hash drifted for {}".format(suite_id)}
        if not str(proof_summary.get("geometry_edit_event_hash_chain", "")).strip():
            return {"status": "fail", "message": "missing geometry edit event hash chain for {}".format(suite_id)}
    return {"status": "pass", "message": "GEO-10 geometry replay matches stress proof surfaces"}
