"""FAST test: MAT-9 inspection applies diegetic epistemic redaction for micro-targeted requests."""

from __future__ import annotations

import copy
import json
import sys


TEST_ID = "testx.materials.epistemic_redaction_applied"
TEST_TAGS = ["fast", "materials", "inspection", "epistemic"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.materialization_testlib import (
        authority_context,
        base_state,
        law_profile,
        policy_context,
        with_structure_aggregate,
    )

    structure_id = "assembly.structure_instance.inspect.redact"
    roi_id = "roi.inspect.redact"
    state = with_structure_aggregate(
        base_state(),
        structure_id=structure_id,
        ag_node_id="ag.node.inspect.redact",
        total_mass=1_600,
        part_count=12,
        batch_id="batch.inspect.redact",
        material_id="material.steel_basic",
    )
    law = law_profile(["process.materialize_structure_roi", "process.inspect_generate_snapshot"])
    admin_authority = authority_context(["entitlement.control.admin"], privilege_level="operator")
    diegetic_authority = authority_context(
        ["entitlement.inspect"],
        privilege_level="observer",
        visibility_level="diegetic",
    )
    policy = policy_context(max_micro_parts_per_roi=64)

    expanded = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.inspect.redact.expand.001",
            "process_id": "process.materialize_structure_roi",
            "inputs": {"structure_instance_id": structure_id, "roi_id": roi_id, "max_micro_parts": 64},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(admin_authority),
        navigation_indices={},
        policy_context=policy,
    )
    if str(expanded.get("result", "")) != "complete":
        return {"status": "fail", "message": "materialization setup failed for epistemic redaction test"}

    micro_ids = sorted(
        str(row.get("micro_part_id", "")).strip()
        for row in list(state.get("micro_part_instances") or [])
        if isinstance(row, dict) and str(row.get("micro_part_id", "")).strip()
    )
    if not micro_ids:
        return {"status": "fail", "message": "materialization setup did not create micro ids for redaction test"}

    inspected = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.inspect.redact.001",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {
                "target_id": "materialization.state.{}::{}".format(structure_id, roi_id),
                "desired_fidelity": "micro",
                "cost_units": 16,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(diegetic_authority),
        navigation_indices={},
        policy_context=policy,
    )
    if str(inspected.get("result", "")) != "complete":
        return {"status": "fail", "message": "diegetic inspection request refused unexpectedly"}

    snapshot = dict(inspected.get("inspection_snapshot") or {})
    snapshot_ext = dict(snapshot.get("extensions") or {})
    if str(snapshot_ext.get("visibility_level", "")).strip() != "diegetic":
        return {"status": "fail", "message": "inspection snapshot visibility_level should be diegetic"}

    sections = dict(snapshot.get("summary_sections") or {})
    if not sections:
        return {"status": "fail", "message": "inspection snapshot missing summary sections"}
    for section in sections.values():
        row = dict(section or {})
        if str(row.get("epistemic_redaction_level", "")).strip() == "none":
            return {"status": "fail", "message": "diegetic inspection section was not redacted"}

    blob = json.dumps(snapshot, sort_keys=True)
    if any(token and token in blob for token in micro_ids):
        return {"status": "fail", "message": "diegetic inspection leaked raw micro part ids"}
    return {"status": "pass", "message": "inspection epistemic redaction passed"}

