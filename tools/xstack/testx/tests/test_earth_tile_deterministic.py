"""FAST test: EARTH-0 Earth tile generation remains deterministic for identical inputs."""

from __future__ import annotations

import sys


TEST_ID = "test_earth_tile_deterministic"
TEST_TAGS = ["fast", "earth", "worldgen", "surface", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth0_testlib import generate_earth_tile_fixture

    first = generate_earth_tile_fixture(repo_root)
    second = generate_earth_tile_fixture(repo_root)
    if first != second:
        return {"status": "fail", "message": "EARTH-0 tile fixture drifted across repeated runs"}
    summary = dict(first.get("surface_summary") or {})
    if str(first.get("surface_handler_id", "")).strip() != "earth.surface.stub":
        return {"status": "fail", "message": "EARTH-0 tile fixture did not route through earth.surface.stub"}
    if str(summary.get("far_lod_visual_class", "")).strip() == "":
        return {"status": "fail", "message": "EARTH-0 tile fixture omitted far-LOD visual classification"}
    return {"status": "pass", "message": "EARTH-0 tile generation deterministic for identical inputs"}
