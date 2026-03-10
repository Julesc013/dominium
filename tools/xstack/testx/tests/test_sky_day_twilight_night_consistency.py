"""FAST test: EARTH-9 day, twilight, and night sky states remain ordered and distinct."""

from __future__ import annotations

import sys


TEST_ID = "test_sky_day_twilight_night_consistency"
TEST_TAGS = ["fast", "earth", "sky", "transition", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth9_testlib import earth_sky_consistency_report

    report = earth_sky_consistency_report(repo_root)
    transition = dict(report.get("sky_transition") or {})
    day = dict(transition.get("day") or {})
    twilight = dict(transition.get("twilight") or {})
    night = dict(transition.get("night") or {})
    if not (int(day.get("sun_intensity_permille", -1)) > int(twilight.get("sun_intensity_permille", -1)) > int(night.get("sun_intensity_permille", -1))):
        return {"status": "fail", "message": "EARTH-9 sun intensity ordering did not follow day > twilight > night"}
    if int(twilight.get("twilight_factor_permille", -1)) <= int(day.get("twilight_factor_permille", -1)):
        return {"status": "fail", "message": "EARTH-9 twilight factor did not strengthen at twilight"}
    if int(night.get("twilight_factor_permille", -1)) != 0:
        return {"status": "fail", "message": "EARTH-9 night sky retained a nonzero twilight factor"}
    view_fingerprints = dict(report.get("view_fingerprints") or {})
    if len(
        {
            str(view_fingerprints.get("sky_day_fingerprint", "")).strip(),
            str(view_fingerprints.get("sky_twilight_fingerprint", "")).strip(),
            str(view_fingerprints.get("sky_night_fingerprint", "")).strip(),
        }
    ) != 3:
        return {"status": "fail", "message": "EARTH-9 sky view fingerprints were not distinct across day/twilight/night"}
    return {"status": "pass", "message": "EARTH-9 sky transitions remain ordered and distinct"}
