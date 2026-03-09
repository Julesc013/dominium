"""FAST test: EARTH-6 ground clamp remains deterministic for identical terrain input."""

from __future__ import annotations

import sys


TEST_ID = "test_ground_clamp_deterministic"
TEST_TAGS = ["fast", "earth", "embodiment", "collision", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth6_testlib import ground_contact_report

    first = ground_contact_report(repo_root)
    second = ground_contact_report(repo_root)
    if str(first.get("result", "")).strip() != "complete" or str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-6 ground-contact fixture did not complete"}
    if first != second:
        return {"status": "fail", "message": "EARTH-6 ground clamp drifted across repeated runs"}
    if int(first.get("transform_z", 0) or 0) != int(first.get("ground_contact_height_mm", 0) or 0):
        return {"status": "fail", "message": "EARTH-6 ground clamp did not snap body transform to contact height"}
    return {"status": "pass", "message": "EARTH-6 ground clamp deterministic"}
