"""FAST test: GEO-10 pathing proof surfaces remain deterministic across topology suites."""

from __future__ import annotations


TEST_ID = "test_pathing_deterministic_across_topologies"
TEST_TAGS = ["fast", "geo", "path", "stress"]


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
    suite_rows = list(stress_report.get("topology_suite_reports") or [])
    if len(suite_rows) < 6:
        return {"status": "fail", "message": "GEO-10 stress report missing topology suites"}
    for row in suite_rows:
        suite_id = str(dict(row).get("suite_id", "")).strip()
        stress_hash = str(dict(dict(row).get("proof_summary") or {}).get("path_result_hash_chain", "")).strip()
        replay_hash = str(dict(replay_rows.get(suite_id) or {}).get("path_result_hash_chain", "")).strip()
        if not stress_hash:
            return {"status": "fail", "message": "missing path_result_hash_chain for {}".format(suite_id)}
        if stress_hash != replay_hash:
            return {"status": "fail", "message": "path hash drifted for {}".format(suite_id)}
    return {"status": "pass", "message": "GEO-10 pathing proof surfaces stable across topology suites"}
