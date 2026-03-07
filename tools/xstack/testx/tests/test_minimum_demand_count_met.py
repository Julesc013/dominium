"""FAST test: player demand matrix includes required minimum breadth."""

from __future__ import annotations


TEST_ID = "test_minimum_demand_count_met"
TEST_TAGS = ["fast", "meta", "genre", "matrix", "coverage"]


def run(repo_root: str):
    from tools.xstack.testx.tests import meta_genre0_testlib

    payload, err = meta_genre0_testlib.load_matrix(repo_root)
    if err:
        return {"status": "fail", "message": "matrix payload missing or invalid"}
    demands = meta_genre0_testlib.matrix_demands(payload)
    if len(demands) < 120:
        return {"status": "fail", "message": "minimum demand count not met (<120)"}
    return {"status": "pass", "message": "minimum demand count met"}
