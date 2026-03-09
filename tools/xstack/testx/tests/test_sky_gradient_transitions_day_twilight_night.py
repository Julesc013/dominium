"""FAST test: EARTH-4 sky gradient transitions remain ordered across day, twilight, and night."""

from __future__ import annotations

import sys


TEST_ID = "test_sky_gradient_transitions_day_twilight_night"
TEST_TAGS = ["fast", "earth", "sky", "gradient", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth4_testlib import sky_gradient_transition_report

    report = sky_gradient_transition_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-4 gradient transition report did not complete"}

    day = dict(report.get("day") or {})
    twilight = dict(report.get("twilight") or {})
    night = dict(report.get("night") or {})

    if not (int(day.get("sun_intensity_permille", -1)) > int(twilight.get("sun_intensity_permille", -1)) > int(night.get("sun_intensity_permille", -1))):
        return {"status": "fail", "message": "EARTH-4 sun intensity ordering did not follow day > twilight > night"}
    if int(twilight.get("twilight_factor_permille", -1)) <= int(day.get("twilight_factor_permille", -1)):
        return {"status": "fail", "message": "EARTH-4 twilight factor did not strengthen at twilight"}
    if int(night.get("twilight_factor_permille", -1)) != 0:
        return {"status": "fail", "message": "EARTH-4 night gradient should resolve to zero twilight factor"}
    return {"status": "pass", "message": "EARTH-4 sky gradient transitions are ordered and stable"}
