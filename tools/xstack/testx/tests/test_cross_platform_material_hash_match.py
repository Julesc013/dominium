"""FAST test: EARTH-10 material proxy sample hash remains stable across platforms."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_material_hash_match"
TEST_TAGS = ["fast", "earth", "material_proxy", "cross_platform", "hash"]
EXPECTED_HASH = "828151ef192eabf39f53a4809bd5685d8dd947b1ca61bf90ec53748fbe30251f"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth10_testlib import earth_material_proxy_hash

    actual_hash = earth_material_proxy_hash(repo_root)
    if not EXPECTED_HASH:
        return {"status": "fail", "message": "EARTH-10 expected material proxy hash fixture is not set"}
    if actual_hash != EXPECTED_HASH:
        return {
            "status": "fail",
            "message": "EARTH-10 material proxy hash drifted: expected {}, got {}".format(EXPECTED_HASH, actual_hash),
        }
    return {"status": "pass", "message": "EARTH-10 material proxy hash matches expected fixture"}
