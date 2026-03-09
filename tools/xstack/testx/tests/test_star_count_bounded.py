"""FAST test: EARTH-4 visible star count remains bounded by policy."""

from __future__ import annotations

import sys


TEST_ID = "test_star_count_bounded"
TEST_TAGS = ["fast", "earth", "sky", "starfield", "budget"]
MAX_STARS = 2048


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth4_testlib import starfield_report

    report = starfield_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-4 star-count report did not complete"}
    star_count = int(report.get("star_count", -1) or -1)
    if star_count < 0:
        return {"status": "fail", "message": "EARTH-4 star-count report omitted star_count"}
    if star_count > MAX_STARS:
        return {"status": "fail", "message": "EARTH-4 star count exceeded policy bound: {}".format(star_count)}
    return {"status": "pass", "message": "EARTH-4 star count remains within the bounded MVP policy"}
