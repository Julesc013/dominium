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
        "SilentMaterialChangeSmell",
        "OrphanBatchSmell",
        "ProvenanceDriftSmell",
        "HardcodedPeriodicTableSmell",
        "MaterialMassDriftSmell",
        "HardcodedBlueprintSmell",
        "NonDeterministicGraphOrderSmell",
        "SilentShipmentSmell",
        "NonDeterministicRoutingSmell",
    ]
    missing = [token for token in required_tokens if token not in text]
    if missing:
        return {
            "status": "fail",
            "message": "missing materials guardrail declaration(s): {}".format(",".join(missing)),
        }

    return {"status": "pass", "message": "materials guardrail declarations present"}
