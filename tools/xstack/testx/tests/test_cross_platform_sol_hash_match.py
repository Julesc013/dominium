"""FAST test: the canonical Sol pin overlay hash stays fixed across platforms."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_sol_hash_match"
TEST_TAGS = ["fast", "sol", "overlay", "cross_platform", "determinism"]

EXPECTED_SOL_HASH = "289e09fd5cd6b9c6c673fe6ccc1e9833865b5c8f8638468fe730b14f1b35e3d5"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.sol0_testlib import build_sol_overlay_fixture, sol_overlay_target_hash

    fixture = build_sol_overlay_fixture(repo_root, refinement_level=2)
    observed_hash = sol_overlay_target_hash(fixture)
    if str(observed_hash).strip().lower() != EXPECTED_SOL_HASH:
        return {
            "status": "fail",
            "message": "Sol overlay hash drifted (expected {}, got {})".format(
                EXPECTED_SOL_HASH,
                observed_hash or "<missing>",
            ),
        }
    return {"status": "pass", "message": "Canonical Sol overlay hash matches the expected cross-platform fixture"}
