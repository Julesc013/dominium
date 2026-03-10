"""FAST test: EMB-2 camera smoothing is deterministic and render-only."""

from __future__ import annotations

import sys


TEST_ID = "test_camera_smoothing_deterministic_render_only"
TEST_TAGS = ["fast", "embodiment", "locomotion", "render"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.emb2_testlib import camera_smoothing_report

    report = camera_smoothing_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EMB-2 camera smoothing probe did not complete"}
    if not bool(report.get("smoothing_applied", False)):
        return {"status": "fail", "message": "EMB-2 third-person smoothing should apply for the probe fixture"}
    if not bool(report.get("body_unchanged", False)):
        return {"status": "fail", "message": "EMB-2 smoothing must remain render-only"}
    if dict(report.get("smoothed_position_mm") or {}) == dict(report.get("target_position_mm") or {}):
        return {"status": "fail", "message": "EMB-2 smoothed camera should differ from the raw target for the probe fixture"}
    return {"status": "pass", "message": "EMB-2 camera smoothing stays deterministic and render-only"}
