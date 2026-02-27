"""FAST test: materials constitutional guardrail declarations are present in docs."""

from __future__ import annotations

import os


TEST_ID = "testx.materials.guardrail_declarations_present"
TEST_TAGS = ["fast", "docs", "materials"]


def run(repo_root: str):
    doc_path = os.path.join(repo_root, "docs", "materials", "GUARDRAIL_DECLARATIONS.md")
    try:
        text = open(doc_path, "r", encoding="utf-8").read()
    except OSError:
        return {"status": "fail", "message": "docs/materials/GUARDRAIL_DECLARATIONS.md missing"}

    required_tokens = [
        "test_batch_lineage_integrity",
        "test_collapse_expand_material_conservation",
        "test_provenance_compaction_integrity",
        "test_commitment_event_required_for_macro_change",
        "test_no_silent_material_mutation",
        "test_element_registry_valid",
        "test_compound_mass_fraction_sum",
        "test_mixture_mass_fraction_sum",
        "test_material_batch_creation_deterministic",
        "test_ledger_mass_tracking_by_material",
        "test_blueprint_compile_deterministic",
        "test_bom_ag_schema_valid",
        "test_instancing_expansion_deterministic",
        "test_missing_part_class_refusal",
        "test_blueprint_visualization_render_model_hash_stable",
        "test_manifest_create_deterministic",
        "test_manifest_tick_delivery_deterministic",
        "test_loss_fraction_deterministic",
        "test_conservation_ledger_transfer_balanced",
        "test_budget_degrade_order_deterministic",
        "test_visual_overlay_render_model_hash_stable",
        "test_project_create_deterministic",
        "test_step_scheduling_deterministic",
        "test_material_consumption_balanced",
        "test_insufficient_material_refusal",
        "test_provenance_events_deterministic",
        "test_visualization_render_model_hash_stable",
        "test_construction_visualization_render_model_hash_stable",
        "test_budget_parallelism_reduction_deterministic",
        "test_decay_deterministic",
        "test_failure_trigger_threshold_deterministic",
        "test_maintenance_reduces_backlog_deterministic",
        "test_inspection_snapshot_cached",
        "test_epistemic_quantization_of_failure_risk",
        "test_time_warp_large_dt_stable",
        "INV-MATERIAL-MUTATION-PROCESS-ONLY",
        "INV-PROVENANCE-REQUIRED",
        "INV-BATCH-LINEAGE-ACYCLIC",
        "INV-NO-MACRO-PART-ENTITIES",
        "INV-MATERIAL-DEFINITIONS-DATA-ONLY",
        "INV-NO-HARDCODED-ELEMENTS",
        "INV-COMPOSITION-VALIDATED",
        "INV-BLUEPRINTS-DATA-ONLY",
        "INV-DETERMINISTIC-BLUEPRINT-COMPILATION",
        "INV-NO-HARDCODED-STRUCTURES",
        "INV-NO-SILENT-TRANSFER",
        "INV-MANIFESTS-PROCESS-ONLY",
        "INV-LOGISTICS-DETERMINISTIC-ROUTING",
        "INV-CONSTRUCTION-REQUIRES-COMMITMENTS",
        "INV-PROVENANCE-EVENTS-REQUIRED",
        "INV-LEDGER-DEBIT-CREDIT-REQUIRED",
        "INV-NO-SILENT-INSTALL",
        "INV-FAILURE-MODES-REGISTRY-DRIVEN",
        "INV-NO-SILENT-FAILURES",
        "INV-MAINTENANCE-IS-COMMITMENT-DRIVEN",
        "SilentMaterialChangeSmell",
        "OrphanBatchSmell",
        "ProvenanceDriftSmell",
        "HardcodedPeriodicTableSmell",
        "MaterialMassDriftSmell",
        "HardcodedBlueprintSmell",
        "NonDeterministicGraphOrderSmell",
        "SilentShipmentSmell",
        "NonDeterministicRoutingSmell",
        "SilentConstructionSmell",
        "MissingProvenanceSmell",
        "SilentFailureSmell",
        "NondeterministicHazardSmell",
    ]
    missing = [token for token in required_tokens if token not in text]
    if missing:
        return {
            "status": "fail",
            "message": "missing materials guardrail declaration(s): {}".format(",".join(missing)),
        }

    return {"status": "pass", "message": "materials guardrail declarations present"}
