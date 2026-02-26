"""STRICT test: expand transitions keep epistemic invariance and refuse forced leakage."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.reality.epistemic_invariance_on_expand"
TEST_TAGS = ["strict", "reality", "transition", "epistemics"]


def _epistemic_check_status(event_row: dict) -> str:
    checks = [dict(item) for item in list(event_row.get("invariant_checks") or []) if isinstance(item, dict)]
    for row in checks:
        if str(row.get("invariant_id", "")).strip() == "inv.epistemic.lod_invariance":
            return str(row.get("status", "")).strip()
    return ""


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.lod_invariance_testlib import base_state, execute_region_transition

    safe_state = copy.deepcopy(base_state())
    safe_expand = execute_region_transition(
        state=safe_state,
        process_id="process.region_expand",
        strict_contracts=True,
        memory_enabled=False,
    )
    if str(safe_expand.get("result", "")) != "complete":
        return {"status": "fail", "message": "safe expand refused unexpectedly under strict contracts"}
    safe_events = [dict(item) for item in list(safe_expand.get("transition_events") or []) if isinstance(item, dict)]
    if len(safe_events) != 1:
        return {"status": "fail", "message": "safe expand did not emit exactly one transition event"}
    if _epistemic_check_status(safe_events[0]) != "pass":
        return {"status": "fail", "message": "safe expand transition event missing pass status for inv.epistemic.lod_invariance"}

    forced_one = execute_region_transition(
        state=copy.deepcopy(base_state()),
        process_id="process.region_expand",
        strict_contracts=True,
        memory_enabled=False,
        force_information_gain=True,
    )
    forced_two = execute_region_transition(
        state=copy.deepcopy(base_state()),
        process_id="process.region_expand",
        strict_contracts=True,
        memory_enabled=False,
        force_information_gain=True,
    )
    if str(forced_one.get("result", "")) != "refused" or str(forced_two.get("result", "")) != "refused":
        return {"status": "fail", "message": "forced information-gain expand did not refuse deterministically"}

    refusal_one = dict(forced_one.get("refusal") or {})
    refusal_two = dict(forced_two.get("refusal") or {})
    if str(refusal_one.get("reason_code", "")).strip() != "refusal.ep.lod_information_gain":
        return {"status": "fail", "message": "forced information-gain expand returned wrong refusal code"}
    if refusal_one != refusal_two:
        return {"status": "fail", "message": "forced information-gain refusal payload diverged across repeated runs"}

    return {"status": "pass", "message": "expand epistemic invariance strict refusal behavior is deterministic"}
