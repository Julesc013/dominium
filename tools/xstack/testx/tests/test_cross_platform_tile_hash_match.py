"""FAST test: MW-3 L3 tile artifact outputs remain fixed for the canonical surface fixture."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_tile_hash_match"
TEST_TAGS = ["fast", "mw", "worldgen", "surface", "cross_platform", "l3"]

EXPECTED_TILE_HASH = "efbc3e731770147f9eea30ffa08fdcd9865ea54bb196a4b5b3283610de0bb166"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.mw3_testlib import generate_surface_fixture_result, surface_result_hash

    _fixture, result = generate_surface_fixture_result(repo_root)
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "MW-3 cross-platform tile fixture did not complete"}
    observed_hash = surface_result_hash(result)
    if str(observed_hash).strip().lower() != EXPECTED_TILE_HASH:
        return {
            "status": "fail",
            "message": "MW-3 L3 tile artifact hash drifted (expected {}, got {})".format(
                EXPECTED_TILE_HASH or "<unset>",
                observed_hash or "<missing>",
            ),
        }
    return {"status": "pass", "message": "MW-3 canonical L3 tile hash matches expected cross-platform fixture"}
