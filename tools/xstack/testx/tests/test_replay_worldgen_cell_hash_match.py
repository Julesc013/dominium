"""FAST test: GEO-8 replay tool reproduces deterministic worldgen hashes."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_replay_worldgen_cell_hash_match"
TEST_TAGS = ["fast", "geo", "worldgen", "replay"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.geo.tool_replay_worldgen_cell import verify_worldgen_cell_replay

    report = verify_worldgen_cell_replay()
    if str(report.get("result", "")) != "complete":
        return {"status": "fail", "message": "worldgen replay verification reported non-complete result"}
    if not bool(report.get("stable_across_repeated_runs", False)):
        return {"status": "fail", "message": "worldgen replay verification was not stable across repeated runs"}
    replay_report = dict(report.get("replay_report") or {})
    observed = dict(replay_report.get("observed") or {})
    recorded = dict(replay_report.get("recorded") or {})
    for key in (
        "generator_version_registry_hash",
        "realism_profile_registry_hash",
        "worldgen_request_hash_chain",
        "worldgen_result_hash_chain",
        "worldgen_spawned_object_hash_chain",
    ):
        token = str(observed.get(key, "")).strip().lower()
        if not _HASH64.fullmatch(token):
            return {"status": "fail", "message": "missing or invalid {}".format(key)}
    if not _HASH64.fullmatch(str(report.get("deterministic_fingerprint", "")).strip().lower()):
        return {"status": "fail", "message": "missing or invalid deterministic_fingerprint"}
    if observed != recorded:
        return {"status": "fail", "message": "worldgen replay observed hashes did not match recorded hashes"}
    return {"status": "pass", "message": "GEO-8 replay tool reproduces deterministic worldgen hashes"}
