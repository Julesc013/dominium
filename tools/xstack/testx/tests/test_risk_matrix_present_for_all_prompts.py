"""FAST test: PI-2 risk matrix covers every planned prompt and all required risk axes."""

from __future__ import annotations


TEST_ID = "test_risk_matrix_present_for_all_prompts"
TEST_TAGS = ["fast", "pi", "blueprint", "risk"]


def run(repo_root: str):
    from tools.xstack.testx.tests.final_prompt_inventory_testlib import (
        committed_final_prompt_inventory,
        committed_prompt_risk_matrix,
    )

    inventory = committed_final_prompt_inventory(repo_root)
    payload = committed_prompt_risk_matrix(repo_root)
    if str(payload.get("report_id", "")).strip() != "pi.2.prompt_risk_matrix.v1":
        return {"status": "fail", "message": "prompt risk matrix report_id drifted"}
    prompts = list(inventory.get("prompts") or [])
    rows = list(payload.get("prompts") or [])
    if len(rows) != len(prompts):
        return {"status": "fail", "message": "prompt risk matrix row count must match prompt count"}
    required_axes = {
        "risk_to_determinism",
        "risk_to_compatibility",
        "risk_to_architecture_drift",
        "risk_to_distribution",
        "risk_to_operator_safety",
        "risk_to_trust_security",
        "aggregate_risk_rating",
    }
    first = dict(rows[0] or {})
    missing = sorted(axis for axis in required_axes if axis not in first)
    if missing:
        return {"status": "fail", "message": f"risk row missing axes: {', '.join(missing)}"}
    if not str(payload.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "prompt risk matrix missing deterministic_fingerprint"}
    return {"status": "pass", "message": "PI-2 risk matrix covers every planned prompt and axis"}
