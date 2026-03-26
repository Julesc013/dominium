"""FAST test: non-runtime helper clusters do not produce secondary convergence actions."""

from __future__ import annotations


TEST_ID = "test_non_runtime_helper_actions_suppressed"
TEST_TAGS = ["fast", "xi", "convergence", "non_runtime"]


def run(repo_root: str):
    from tools.xstack.testx.tests.convergence_plan_testlib import committed_convergence_actions

    payload = committed_convergence_actions(repo_root)
    actions = list(payload.get("actions") or [])
    blocked_clusters = {
        "duplicate.cluster.048b5761cad48449",
        "duplicate.cluster.04a1e5211585a96a",
        "duplicate.cluster.04cf87063ec876a1",
    }
    offenders = [
        dict(row)
        for row in actions
        if str(dict(row).get("cluster_id", "")).strip() in blocked_clusters
        and str(dict(row).get("kind", "")).strip() != "keep"
    ]
    if offenders:
        sample = offenders[0]
        return {
            "status": "fail",
            "message": "non-runtime helper clusters must not produce secondary actions: "
            f"{sample.get('symbol_name')} -> {sample.get('kind')}",
        }
    return {"status": "pass", "message": "non-runtime helper clusters are suppressed from secondary convergence actions"}
