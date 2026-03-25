"""FAST test: XI-3 decision-rule ordering stays stable on regeneration."""

from __future__ import annotations


TEST_ID = "test_decision_rules_stable"
TEST_TAGS = ["fast", "xi", "duplicates", "convergence"]


def run(repo_root: str):
    from tools.xstack.testx.tests.convergence_plan_testlib import committed_convergence_actions, fresh_snapshot

    committed = committed_convergence_actions(repo_root)
    fresh = dict(fresh_snapshot(repo_root).get("convergence_actions") or {})
    committed_actions = committed.get("actions") or []
    fresh_actions = fresh.get("actions") or []
    if len(committed_actions) != len(fresh_actions):
        return {"status": "fail", "message": "XI-3 action count changed after deterministic regeneration"}
    committed_keys = [
        (
            str(row.get("cluster_id", "")).strip(),
            str(row.get("kind", "")).strip(),
            str(row.get("canonical_file", "")).strip(),
            str(row.get("secondary_file", "")).strip(),
        )
        for row in committed_actions
    ]
    fresh_keys = [
        (
            str(row.get("cluster_id", "")).strip(),
            str(row.get("kind", "")).strip(),
            str(row.get("canonical_file", "")).strip(),
            str(row.get("secondary_file", "")).strip(),
        )
        for row in fresh_actions
    ]
    if committed_keys != fresh_keys:
        return {"status": "fail", "message": "XI-3 decision-rule ordering drifted on regeneration"}
    return {"status": "pass", "message": "XI-3 decision-rule ordering is stable"}
