"""FAST test: GEO-6 replay verifier produces stable path hash chains."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_cross_platform_path_hash_match"
TEST_TAGS = ["fast", "geo", "path", "replay", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.geo.tool_replay_path_request import verify_path_request_replay

    first = verify_path_request_replay()
    second = verify_path_request_replay()
    if dict(first) != dict(second):
        return {"status": "fail", "message": "path replay verifier is not deterministic"}
    for key in ("path_request_hash_chain", "path_result_hash_chain", "traversal_policy_registry_hash", "deterministic_fingerprint"):
        token = str(first.get(key, "")).strip().lower()
        if not _HASH64.fullmatch(token):
            return {"status": "fail", "message": "missing or invalid {}".format(key)}
    if str(first.get("result", "")) != "complete":
        return {"status": "fail", "message": "path replay verifier reported non-complete result"}
    return {"status": "pass", "message": "GEO-6 path replay hash chains stable"}
