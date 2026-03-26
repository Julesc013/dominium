"""FAST test: PI-1 phase ordering remains stable and internally coherent."""

from __future__ import annotations


TEST_ID = "test_foundation_phase_order_consistent"
TEST_TAGS = ["fast", "pi", "blueprint", "phases"]


def run(repo_root: str):
    from tools.xstack.testx.tests.series_execution_strategy_testlib import committed_foundation_phases

    payload = committed_foundation_phases(repo_root)
    phases = list(payload.get("phases") or [])
    phase_ids = [str(dict(row).get("phase_id", "")).strip() for row in phases]
    if phase_ids != ["A", "B", "C", "D", "E"]:
        return {"status": "fail", "message": "foundation phase order drifted"}
    phase_map = {str(dict(row).get("phase_id", "")).strip(): dict(row) for row in phases}
    phase_d_prereqs = " ".join(str(item).strip() for item in phase_map["D"].get("prerequisites") or [])
    phase_e_prereqs = " ".join(str(item).strip() for item in phase_map["E"].get("prerequisites") or [])
    if "Phase A complete" not in phase_d_prereqs or "Phase B complete" not in phase_d_prereqs or "Phase C complete" not in phase_d_prereqs:
        return {"status": "fail", "message": "phase D must depend on phases A, B, and C"}
    if "Phase D complete" not in phase_e_prereqs:
        return {"status": "fail", "message": "phase E must depend on phase D"}
    return {"status": "pass", "message": "PI-1 phase ordering is stable and coherent"}
