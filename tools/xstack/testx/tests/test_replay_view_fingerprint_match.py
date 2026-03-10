"""FAST test: EARTH-9 replayed view fingerprints match the regression lock."""

from __future__ import annotations

import sys


TEST_ID = "test_replay_view_fingerprint_match"
TEST_TAGS = ["fast", "earth", "view", "replay", "regression"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth9_testlib import earth_view_fingerprint_report

    report = earth_view_fingerprint_report(repo_root)
    baseline = dict(report.get("baseline") or {})
    replay = dict(report.get("view_replay") or {})
    if str(replay.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-9 replayed view window did not complete"}
    baseline_views = dict(baseline.get("view_fingerprints") or {})
    replay_views = dict(replay.get("view_fingerprints") or {})
    expected_map = {
        "day_sky_view": "sky_day_fingerprint",
        "twilight_sky_view": "sky_twilight_fingerprint",
        "night_sky_view": "sky_night_fingerprint",
        "day_lighting_view": "lighting_day_fingerprint",
        "twilight_lighting_view": "lighting_twilight_fingerprint",
        "night_lighting_view": "lighting_night_fingerprint",
        "water_view": "water_view_fingerprint",
        "map_view": "map_view_fingerprint",
    }
    for baseline_key, replay_key in sorted(expected_map.items()):
        if str(baseline_views.get(baseline_key, "")).strip() != str(replay_views.get(replay_key, "")).strip():
            return {
                "status": "fail",
                "message": "EARTH-9 replay fingerprint mismatch for '{}'".format(baseline_key),
            }
    return {"status": "pass", "message": "EARTH-9 replayed view fingerprints match the regression lock"}
