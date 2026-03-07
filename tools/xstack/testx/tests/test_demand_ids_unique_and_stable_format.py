"""FAST test: demand IDs are unique and match stable prefixed snake_case format."""

from __future__ import annotations

import re


TEST_ID = "test_demand_ids_unique_and_stable_format"
TEST_TAGS = ["fast", "meta", "genre", "matrix", "identity"]


DEMAND_ID_RE = re.compile(r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*(?:_[a-z0-9_]+)*$")


def run(repo_root: str):
    from tools.xstack.testx.tests import meta_genre0_testlib

    payload, err = meta_genre0_testlib.load_matrix(repo_root)
    if err:
        return {"status": "fail", "message": "matrix payload missing or invalid"}

    demands = meta_genre0_testlib.matrix_demands(payload)
    seen = set()
    for row in demands:
        demand_id = str(row.get("demand_id", "")).strip()
        if not demand_id:
            return {"status": "fail", "message": "empty demand_id encountered"}
        if not DEMAND_ID_RE.fullmatch(demand_id):
            return {"status": "fail", "message": "invalid demand_id format: {}".format(demand_id)}
        if demand_id in seen:
            return {"status": "fail", "message": "duplicate demand_id: {}".format(demand_id)}
        seen.add(demand_id)
    return {"status": "pass", "message": "demand IDs are unique and stable"}
