"""FAST test: yanked candidates stay excluded from latest-compatible update simulation."""

from __future__ import annotations


TEST_ID = "test_yanked_excluded"
TEST_TAGS = ["fast", "release", "update", "omega"]


def run(repo_root: str):
    from tools.xstack.testx.tests.update_sim_testlib import build_report

    report = build_report(repo_root, suffix="yanked_excluded")
    scenario = dict(report.get("yanked_candidate_exclusion") or {})
    if str(scenario.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "yanked exclusion scenario must complete"}
    if list(scenario.get("selected_yanked_component_ids") or []):
        return {"status": "fail", "message": "latest-compatible update simulation must not select yanked candidates"}
    if int(scenario.get("skipped_yanked_count", 0) or 0) < 1:
        return {"status": "fail", "message": "yanked exclusion scenario must log the skipped yanked candidate"}
    return {"status": "pass", "message": "yanked candidates are excluded deterministically"}
