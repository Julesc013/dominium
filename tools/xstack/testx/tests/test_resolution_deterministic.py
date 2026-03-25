"""FAST test: Omega ecosystem resolution is deterministic across repeated runs."""

from __future__ import annotations

import sys


TEST_ID = "test_resolution_deterministic"
TEST_TAGS = ["fast", "omega", "ecosystem", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.mvp.ecosystem_verify_common import verify_ecosystem

    first = verify_ecosystem(repo_root)
    second = verify_ecosystem(repo_root)
    if first != second:
        return {"status": "fail", "message": "ecosystem verifier drifted across repeated identical runs"}
    return {"status": "pass", "message": "ecosystem verifier is deterministic across repeated runs"}
