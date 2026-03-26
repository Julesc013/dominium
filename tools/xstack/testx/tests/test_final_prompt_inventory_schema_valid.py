"""FAST test: PI-2 final prompt inventory exposes the full planned prompt catalog."""

from __future__ import annotations


TEST_ID = "test_final_prompt_inventory_schema_valid"
TEST_TAGS = ["fast", "pi", "blueprint", "inventory"]


def run(repo_root: str):
    from tools.xstack.testx.tests.final_prompt_inventory_testlib import committed_final_prompt_inventory

    payload = committed_final_prompt_inventory(repo_root)
    if str(payload.get("report_id", "")).strip() != "pi.2.final_prompt_inventory.v1":
        return {"status": "fail", "message": "final prompt inventory report_id drifted"}
    prompts = list(payload.get("prompts") or [])
    if len(prompts) != 110:
        return {"status": "fail", "message": f"expected 110 future prompts, found {len(prompts)}"}
    required_keys = {
        "prompt_id",
        "series_id",
        "title",
        "short_goal",
        "prerequisites",
        "dependent_prompts",
        "risk_level",
        "execution_class",
        "snapshot_requirement",
        "gate_profile_required",
        "rollback_strategy_required",
        "manual_review_required",
        "stop_conditions",
    }
    first = dict(prompts[0] or {})
    missing = sorted(key for key in required_keys if key not in first)
    if missing:
        return {"status": "fail", "message": f"prompt row missing required keys: {', '.join(missing)}"}
    stop_rows = list(payload.get("global_stop_conditions") or [])
    if len(stop_rows) < 6:
        return {"status": "fail", "message": "global stop conditions are incomplete"}
    if not str(payload.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "final prompt inventory missing deterministic_fingerprint"}
    return {"status": "pass", "message": "PI-2 final prompt inventory exposes the full planned prompt catalog"}
