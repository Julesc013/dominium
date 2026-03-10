"""FAST test: compiled logic preference falls back to L1 evaluation."""

from __future__ import annotations


TEST_ID = "test_compiled_logic_falls_back_to_l1_eval"
TEST_TAGS = ["fast", "compat", "cap_neg", "degrade"]


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg3_testlib import compiled_fallback_negotiation

    result = compiled_fallback_negotiation(repo_root)
    record = dict(result.get("negotiation_record") or {})
    substitutions = list(record.get("substituted_capabilities") or [])
    target = None
    for row in substitutions:
        if str((dict(row or {})).get("capability_id", "")) == "cap.logic.compiled_automaton":
            target = str((dict(row or {})).get("substitute_capability_id", "")).strip()
            break
    if target != "cap.logic.l1_eval":
        return {"status": "fail", "message": "compiled logic did not fall back to cap.logic.l1_eval"}
    return {"status": "pass", "message": "compiled logic preference falls back to L1 evaluation"}
