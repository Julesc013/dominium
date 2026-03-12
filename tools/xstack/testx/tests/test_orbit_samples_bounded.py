"""FAST test: SOL-2 orbit samples remain within policy bounds."""

from __future__ import annotations

import sys


TEST_ID = "test_orbit_samples_bounded"
TEST_TAGS = ["fast", "sol", "orbit", "bounds", "policy"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sol2_testlib import orbit_replay_report_payload

    report = orbit_replay_report_payload(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "SOL-2 orbit replay did not complete"}
    expected_samples = int(report.get("expected_samples_per_orbit", 0) or 0)
    expected_max_paths = int(report.get("expected_max_paths_per_view", 0) or 0)
    if expected_samples <= 0 or expected_max_paths <= 0:
        return {"status": "fail", "message": "SOL-2 orbit sampling policy is invalid"}
    sample_counts = dict(report.get("sample_counts") or {})
    for chart_name, chart_rows in sorted(sample_counts.items()):
        for object_id, count in sorted(dict(chart_rows or {}).items()):
            if int(count) != expected_samples:
                return {
                    "status": "fail",
                    "message": "SOL-2 {} sample count drifted for {}: expected {}, got {}".format(
                        chart_name,
                        object_id,
                        expected_samples,
                        count,
                    ),
                }
    path_counts = dict(report.get("path_counts") or {})
    for chart_name, count in sorted(path_counts.items()):
        if int(count) > expected_max_paths:
            return {
                "status": "fail",
                "message": "SOL-2 {} path count exceeded the policy: {} > {}".format(
                    chart_name,
                    count,
                    expected_max_paths,
                ),
            }
    if list(dict(report.get("positions") or {}).get("earth_local", {}).get("sol.planet.earth", [])) != [0, 0, 0]:
        return {"status": "fail", "message": "SOL-2 earth-local orbit chart no longer centers Earth at the origin"}
    return {"status": "pass", "message": "SOL-2 orbit samples remain within policy bounds"}
