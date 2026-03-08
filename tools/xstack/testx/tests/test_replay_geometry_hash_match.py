"""FAST test: GEO-7 replay tool reproduces deterministic geometry hashes."""

from __future__ import annotations

import sys


TEST_ID = "test_replay_geometry_hash_match"
TEST_TAGS = ["fast", "geo", "geometry", "replay"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.geo.tool_replay_geometry_window import verify_geometry_window_fixture

    report = verify_geometry_window_fixture()
    if str(report.get("result", "")) != "complete":
        return {"status": "fail", "message": "geometry replay verification reported non-complete result"}
    if not bool(report.get("stable_across_repeated_runs", False)):
        return {"status": "fail", "message": "geometry replay verification was not stable across repeated runs"}
    replay_report = dict(report.get("replay_report") or {})
    observed = dict(replay_report.get("observed") or {})
    recorded = dict(replay_report.get("recorded") or {})
    if str(observed.get("geometry_edit_policy_registry_hash", "")) != str(recorded.get("geometry_edit_policy_registry_hash", "")):
        return {"status": "fail", "message": "geometry edit policy registry hash did not match recorded runtime output"}
    if not str(report.get("geometry_state_hash_chain", "")).strip():
        return {"status": "fail", "message": "geometry replay verification did not produce geometry_state_hash_chain"}
    if not str(report.get("geometry_edit_event_hash_chain", "")).strip():
        return {"status": "fail", "message": "geometry replay verification did not produce geometry_edit_event_hash_chain"}
    return {"status": "pass", "message": "GEO-7 replay tool reproduces deterministic geometry hashes"}
