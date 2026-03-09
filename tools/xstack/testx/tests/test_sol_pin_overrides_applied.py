"""FAST test: the official Sol pin overlay applies the expected canonical overrides."""

from __future__ import annotations

import sys


TEST_ID = "test_sol_pin_overrides_applied"
TEST_TAGS = ["fast", "sol", "overlay", "pack"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.sol0_testlib import build_sol_overlay_fixture, effective_object_map

    fixture = build_sol_overlay_fixture(repo_root, refinement_level=2)
    slot_ids = dict(fixture.get("patch_document", {}).get("slot_object_ids") or {})
    merged = effective_object_map(dict(fixture.get("merge_result") or {}).get("effective_object_views"))
    sol_system = dict(merged.get(str(slot_ids.get("sol.system", "")).strip()) or {}).get("properties", {})
    sol_star = dict(merged.get(str(slot_ids.get("sol.star", "")).strip()) or {}).get("properties", {})
    earth = dict(merged.get(str(slot_ids.get("sol.planet.earth", "")).strip()) or {}).get("properties", {})
    luna = dict(merged.get(str(slot_ids.get("sol.moon.luna", "")).strip()) or {}).get("properties", {})
    if str(dict(sol_system).get("display_name", "")).strip() != "Sol":
        return {"status": "fail", "message": "Sol system display_name was not pinned by the official overlay"}
    if int(dict(dict(sol_star).get("physical") or {}).get("radius_km", 0) or 0) != 695700:
        return {"status": "fail", "message": "Sol star radius was not pinned by the official overlay"}
    if int(dict(dict(earth).get("physical") or {}).get("radius_km", 0) or 0) != 6371:
        return {"status": "fail", "message": "Earth radius was not pinned by the official overlay"}
    if str(dict(luna).get("display_name", "")).strip() != "Luna":
        return {"status": "fail", "message": "Luna was not materialized by the official overlay"}
    return {"status": "pass", "message": "Official Sol pin overrides applied to the canonical target set"}

