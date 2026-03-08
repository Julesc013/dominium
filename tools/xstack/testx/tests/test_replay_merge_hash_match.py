"""FAST test: GEO-9 replay tool reproduces deterministic overlay merge hashes."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_replay_merge_hash_match"
TEST_TAGS = ["fast", "geo", "overlay", "replay"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.geo.tool_replay_overlay_merge import verify_overlay_merge_fixture

    report = verify_overlay_merge_fixture()
    if str(report.get("result", "")) != "complete":
        return {"status": "fail", "message": "overlay replay verification reported non-complete result"}
    if not bool(report.get("stable_across_repeated_runs", False)):
        return {"status": "fail", "message": "overlay replay verification was not stable across repeated runs"}
    replay_report = dict(report.get("replay_report") or {})
    observed = dict(replay_report.get("observed") or {})
    recorded = dict(replay_report.get("recorded") or {})
    for key in (
        "overlay_policy_registry_hash",
        "overlay_manifest_hash",
        "property_patch_hash_chain",
        "overlay_merge_result_hash_chain",
    ):
        token = str(observed.get(key, "")).strip().lower()
        if not _HASH64.fullmatch(token):
            return {"status": "fail", "message": "missing or invalid {}".format(key)}
    if observed.get("overlay_manifest_hash") != recorded.get("overlay_manifest_hash"):
        return {"status": "fail", "message": "overlay manifest hash did not replay-match"}
    if observed.get("property_patch_hash_chain") != recorded.get("property_patch_hash_chain"):
        return {"status": "fail", "message": "property patch hash chain did not replay-match"}
    if observed.get("overlay_merge_result_hash_chain") != recorded.get("overlay_merge_result_hash_chain"):
        return {"status": "fail", "message": "overlay merge result hash chain did not replay-match"}
    if not _HASH64.fullmatch(str(report.get("deterministic_fingerprint", "")).strip().lower()):
        return {"status": "fail", "message": "missing or invalid deterministic_fingerprint"}
    return {"status": "pass", "message": "GEO-9 replay tool reproduces deterministic overlay merge hashes"}
