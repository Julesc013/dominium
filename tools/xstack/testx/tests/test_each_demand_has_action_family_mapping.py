"""FAST test: each demand declares non-empty action family mapping."""

from __future__ import annotations


TEST_ID = "test_each_demand_has_action_family_mapping"
TEST_TAGS = ["fast", "meta", "genre", "matrix", "action"]


def run(repo_root: str):
    from tools.xstack.testx.tests import meta_genre0_testlib

    payload, err = meta_genre0_testlib.load_matrix(repo_root)
    if err:
        return {"status": "fail", "message": "matrix payload missing or invalid"}
    demands = meta_genre0_testlib.matrix_demands(payload)
    for row in demands:
        demand_id = str(row.get("demand_id", "")).strip() or "<unknown>"
        families = [str(token).strip() for token in list(row.get("action_families") or []) if str(token).strip()]
        if not families:
            return {"status": "fail", "message": "{} missing action_families mapping".format(demand_id)}
    return {"status": "pass", "message": "all demands include action family mapping"}
