"""FAST test: GEO-5 replay tool reproduces the same projected-view fingerprint and registry hashes."""

from __future__ import annotations

import sys


TEST_ID = "test_replay_view_fingerprint_match"
TEST_TAGS = ["fast", "geo", "projection", "replay"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.geo import lens_layer_registry_hash, projection_profile_registry_hash, view_type_registry_hash
    from tools.geo.tool_replay_view_window import verify_view_window

    report = verify_view_window()
    if str(report.get("result", "")) != "complete":
        return {"status": "fail", "message": "view replay verification reported non-complete result"}
    if not bool(report.get("stable_across_repeated_runs", False)):
        return {"status": "fail", "message": "view replay verification was not stable across repeated runs"}
    if str(report.get("projection_profile_registry_hash", "")) != projection_profile_registry_hash():
        return {"status": "fail", "message": "projection profile registry hash did not match replay tool output"}
    if str(report.get("lens_layer_registry_hash", "")) != lens_layer_registry_hash():
        return {"status": "fail", "message": "lens layer registry hash did not match replay tool output"}
    if str(report.get("view_type_registry_hash", "")) != view_type_registry_hash():
        return {"status": "fail", "message": "view type registry hash did not match replay tool output"}
    observed = dict(report.get("observed") or {})
    if not str(observed.get("view_fingerprint", "")).strip():
        return {"status": "fail", "message": "view replay verification did not produce a view fingerprint"}
    return {"status": "pass", "message": "GEO-5 replay tool reproduces deterministic view fingerprints"}
