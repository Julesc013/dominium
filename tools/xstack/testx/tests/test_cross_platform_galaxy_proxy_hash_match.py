"""FAST test: GAL-0 galaxy proxy replay hash remains stable across platforms."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_galaxy_proxy_hash_match"
TEST_TAGS = ["fast", "galaxy", "proxy", "cross_platform", "hash"]
EXPECTED_HASH = "e5aff9a414dbe2e713e5a4def71039de453a77cdbc6aa3fa858304fe31162616"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.gal0_testlib import galaxy_proxy_hash

    actual_hash = galaxy_proxy_hash(repo_root)
    if not EXPECTED_HASH:
        return {"status": "fail", "message": "GAL-0 expected galaxy proxy hash fixture is not set"}
    if actual_hash != EXPECTED_HASH:
        return {
            "status": "fail",
            "message": "GAL-0 galaxy proxy hash drifted: expected {}, got {}".format(EXPECTED_HASH, actual_hash),
        }
    return {"status": "pass", "message": "GAL-0 galaxy proxy hash matches expected fixture"}
