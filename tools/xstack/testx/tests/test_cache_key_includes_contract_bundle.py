"""FAST test: MW-4 cache keys include semantic contract pins."""

from __future__ import annotations

import sys


TEST_ID = "test_cache_key_includes_contract_bundle"
TEST_TAGS = ["fast", "mw4", "worldgen", "cache", "compat"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.worldgen.refinement.refinement_cache import build_refinement_cache_key
    from tools.xstack.testx.tests.geo8_testlib import worldgen_cell_key

    common = {
        "universe_identity_hash": "identity.hash.mw4",
        "generator_version_id": "gen.v0_stub",
        "realism_profile_id": "realism.realistic_default_milkyway_stub",
        "overlay_manifest_hash": "overlay.hash.mw4",
        "mod_policy_id": "mod_policy.strict",
        "geo_cell_key": worldgen_cell_key([9, 1, -4]),
        "refinement_level": 2,
    }
    first = build_refinement_cache_key(
        universe_contract_bundle_hash="bundle.contract.a",
        **common,
    )
    second = build_refinement_cache_key(
        universe_contract_bundle_hash="bundle.contract.b",
        **common,
    )
    if first == second:
        return {"status": "fail", "message": "cache key ignored universe_contract_bundle_hash"}
    return {"status": "pass", "message": "MW-4 cache keys include contract bundle pins"}
