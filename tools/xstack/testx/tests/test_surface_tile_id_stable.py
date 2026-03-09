"""FAST test: MW-3 surface tile identities remain stable for identical tile requests."""

from __future__ import annotations

import sys


TEST_ID = "test_surface_tile_id_stable"
TEST_TAGS = ["fast", "mw", "worldgen", "surface", "identity"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.mw3_testlib import generate_surface_fixture_result

    _fixture, first = generate_surface_fixture_result(repo_root)
    _fixture, second = generate_surface_fixture_result(repo_root)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "MW-3 surface tile fixture did not complete"}
    first_rows = list(first.get("generated_surface_tile_artifact_rows") or [])
    second_rows = list(second.get("generated_surface_tile_artifact_rows") or [])
    if first_rows != second_rows:
        return {"status": "fail", "message": "MW-3 surface tile artifact rows drifted across repeated runs"}
    if len(first_rows) != 1:
        return {"status": "fail", "message": "MW-3 surface tile fixture did not produce exactly one tile artifact"}
    if str(dict(first_rows[0]).get("tile_object_id", "")).strip() == "":
        return {"status": "fail", "message": "MW-3 surface tile artifact omitted tile_object_id"}
    return {"status": "pass", "message": "MW-3 surface tile identities stable across identical tile requests"}
