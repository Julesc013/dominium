"""FAST test: PI-2 snapshot mapping template contains one deterministic row per prompt."""

from __future__ import annotations


TEST_ID = "test_snapshot_mapping_template_schema_valid"
TEST_TAGS = ["fast", "pi", "blueprint", "snapshot"]


def run(repo_root: str):
    from tools.xstack.testx.tests.final_prompt_inventory_testlib import (
        committed_final_prompt_inventory,
        committed_snapshot_mapping_template,
    )

    inventory = committed_final_prompt_inventory(repo_root)
    payload = committed_snapshot_mapping_template(repo_root)
    if str(payload.get("report_id", "")).strip() != "pi.2.snapshot_mapping_template.v1":
        return {"status": "fail", "message": "snapshot mapping template report_id drifted"}
    rows = list(payload.get("rows") or [])
    prompts = list(inventory.get("prompts") or [])
    if len(rows) != len(prompts):
        return {"status": "fail", "message": "snapshot mapping row count must match prompt count"}
    required_fields = {
        "planned_module_targets",
        "actual_repo_locations",
        "gaps_found",
        "drift_found",
        "obsolete_assumptions",
        "keep_merge_replace_recommendation",
        "confidence_score",
        "requires_manual_review",
    }
    first = dict(rows[0] or {})
    missing = sorted(field for field in required_fields if field not in first)
    if missing:
        return {"status": "fail", "message": f"snapshot mapping row missing fields: {', '.join(missing)}"}
    if list(payload.get("template_fields") or []) != [
        "planned_module_targets",
        "actual_repo_locations",
        "gaps_found",
        "drift_found",
        "obsolete_assumptions",
        "keep_merge_replace_recommendation",
        "confidence_score",
        "requires_manual_review",
    ]:
        return {"status": "fail", "message": "snapshot mapping template fields drifted"}
    return {"status": "pass", "message": "PI-2 snapshot mapping template is complete and deterministic"}
