"""FAST test: the Sol anchor cell always yields the canonical base system when requested."""

from __future__ import annotations

import sys


TEST_ID = "test_sol_anchor_exists_when_requested"
TEST_TAGS = ["fast", "sol", "overlay", "worldgen", "anchor"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.sol0_testlib import build_sol_overlay_fixture

    fixture = build_sol_overlay_fixture(repo_root, refinement_level=2)
    summary = dict(fixture.get("worldgen_result", {}).get("mw_cell_summary") or {})
    summary_ext = dict(summary.get("extensions") or {})
    if "sol.system" not in list(fixture.get("existing_slot_ids") or []):
        return {"status": "fail", "message": "Sol anchor request did not produce the canonical base star system"}
    if not bool(summary_ext.get("sol_anchor_active")):
        return {"status": "fail", "message": "Sol anchor summary did not mark the requested cell as the active Sol anchor"}
    return {"status": "pass", "message": "Sol anchor request yields the canonical base star system"}

