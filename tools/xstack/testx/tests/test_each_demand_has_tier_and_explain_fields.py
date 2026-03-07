"""FAST test: each demand declares tier requirements and explain hooks."""

from __future__ import annotations


TEST_ID = "test_each_demand_has_tier_and_explain_fields"
TEST_TAGS = ["fast", "meta", "genre", "matrix", "tier", "explain"]


def run(repo_root: str):
    from tools.xstack.testx.tests import meta_genre0_testlib

    payload, err = meta_genre0_testlib.load_matrix(repo_root)
    if err:
        return {"status": "fail", "message": "matrix payload missing or invalid"}
    demands = meta_genre0_testlib.matrix_demands(payload)
    for row in demands:
        demand_id = str(row.get("demand_id", "")).strip() or "<unknown>"
        tiers = [str(token).strip() for token in list(row.get("tiers") or []) if str(token).strip()]
        explain = [str(token).strip() for token in list(row.get("explain") or []) if str(token).strip()]
        if not tiers:
            return {"status": "fail", "message": "{} missing tiers".format(demand_id)}
        if not explain:
            return {"status": "fail", "message": "{} missing explain hooks".format(demand_id)}
    return {"status": "pass", "message": "all demands include tiers and explain hooks"}
