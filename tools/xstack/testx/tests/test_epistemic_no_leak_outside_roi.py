"""FAST test: diegetic inspection payload redacts micro identifiers for materialization state."""

from __future__ import annotations

import json
import sys


TEST_ID = "testx.materials.epistemic_no_leak_outside_roi"
TEST_TAGS = ["fast", "materials", "materialization", "epistemic"]


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

    structure_id = "assembly.structure_instance.delta"
    roi_id = "roi.delta"
    state = with_structure_aggregate(
        base_state(),
        structure_id=structure_id,
        ag_node_id="ag.node.delta",
        total_mass=800,
        part_count=8,
        batch_id="batch.delta",
        material_id="material.steel_basic",
    )
    law = law_profile(["process.materialize_structure_roi", "process.inspect_generate_snapshot"])
    admin_authority = authority_context(["entitlement.control.admin"], privilege_level="operator")
    policy = policy_context(max_micro_parts_per_roi=64)

    expanded = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materialize.delta.001",
            "process_id": "process.materialize_structure_roi",
            "inputs": {"structure_instance_id": structure_id, "roi_id": roi_id, "max_micro_parts": 64},
        },
        law_profile=law,
        authority_context=admin_authority,
        navigation_indices={},
        policy_context=policy,
    )
    if str(expanded.get("result", "")) != "complete":
        return {"status": "fail", "message": "materialization setup failed for epistemic leak test"}
    micro_ids = sorted(
        str(row.get("micro_part_id", "")).strip()
        for row in list(state.get("micro_part_instances") or [])
        if isinstance(row, dict) and str(row.get("micro_part_id", "")).strip()
    )
    if not micro_ids:
        return {"status": "fail", "message": "materialization setup produced no micro ids for leak verification"}

    diegetic_authority = authority_context(
        ["entitlement.inspect"],
        privilege_level="observer",
        visibility_level="diegetic",
    )
    inspected = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.inspect.delta.001",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {"target_id": "materialization.state.{}::{}".format(structure_id, roi_id)},
        },
        law_profile=law,
        authority_context=diegetic_authority,
        navigation_indices={},
        policy_context=policy,
    )
    if str(inspected.get("result", "")) != "complete":
        return {"status": "fail", "message": "diegetic inspect_generate_snapshot failed"}
    snapshot = dict((dict(inspected.get("result_metadata") or {})).get("inspection_snapshot") or {})
    target_payload = dict(snapshot.get("target_payload") or {})
    row = dict(target_payload.get("row") or {})
    if list(row.get("materialized_part_ids") or []):
        return {"status": "fail", "message": "diegetic inspection leaked materialized_part_ids"}
    snapshot_blob = json.dumps(snapshot, sort_keys=True)
    if any(token and token in snapshot_blob for token in micro_ids):
        return {"status": "fail", "message": "diegetic inspection leaked raw micro_part_id values"}

    from tools.xstack.sessionx.observation import build_truth_model, observe_truth

    truth_model = build_truth_model(
        universe_identity={"schema_version": "1.0.0", "identity_id": "identity.test.materialization"},
        universe_state=state,
        lockfile_payload={"registries": {}},
        identity_path="identity.test.materialization.json",
        state_path="state.test.materialization.json",
        registry_payloads={
            "epistemic_policy_registry": {
                "policies": [
                    {
                        "epistemic_policy_id": "ep.policy.lab_broad",
                        "retention_policy_id": "ep.retention.session_basic",
                        "allowed_observation_channels": ["ch.core.entities"],
                        "forbidden_channels": [],
                        "inference_policy_id": "ep.infer.none",
                        "max_precision_rules": [],
                        "deterministic_filters": [],
                        "extensions": {},
                    }
                ]
            },
            "retention_policy_registry": {
                "policies": [
                    {
                        "retention_policy_id": "ep.retention.session_basic",
                        "memory_allowed": True,
                        "max_memory_items": 256,
                        "decay_model_id": "ep.decay.session_basic",
                        "eviction_rule_id": "evict.oldest_first",
                        "deterministic_eviction_rule_id": "evict.oldest_first",
                        "extensions": {},
                    }
                ]
            },
            "decay_model_registry": {
                "decay_models": [
                    {
                        "decay_model_id": "ep.decay.session_basic",
                        "formula_kind": "none",
                        "parameters": {},
                        "extensions": {},
                    }
                ]
            },
            "eviction_rule_registry": {
                "eviction_rules": [
                    {
                        "eviction_rule_id": "evict.oldest_first",
                        "algorithm": "oldest_first",
                        "deterministic_tie_break": "id_asc",
                        "extensions": {},
                    }
                ]
            },
        },
    )
    observed = observe_truth(
        truth_model=truth_model,
        lens={
            "lens_id": "lens.diegetic.sensor",
            "lens_type": "diegetic",
            "required_entitlements": [],
            "epistemic_constraints": {"visibility_policy": "diegetic"},
            "observation_channels": ["ch.core.entities"],
        },
        law_profile=law,
        authority_context=diegetic_authority,
        viewpoint_id="viewpoint.test.materialization",
    )
    if str(observed.get("result", "")) != "complete":
        return {"status": "fail", "message": "observe_truth failed during epistemic leak validation"}
    perceived = dict(observed.get("perceived_model") or {})
    entity_rows = list((dict(perceived.get("entities") or {})).get("entries") or [])
    for entity_row in entity_rows:
        token = str((dict(entity_row).get("semantic_id") or dict(entity_row).get("entity_id") or "")).strip()
        if token.startswith("micro.part."):
            return {"status": "fail", "message": "PerceivedModel leaked micro part semantic ids outside ROI"}
    return {"status": "pass", "message": "diegetic materialization inspection redaction passed"}
