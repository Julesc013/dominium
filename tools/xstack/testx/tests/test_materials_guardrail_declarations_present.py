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
        "INV-MATERIAL-MUTATION-PROCESS-ONLY",
        "INV-PROVENANCE-REQUIRED",
        "INV-BATCH-LINEAGE-ACYCLIC",
        "INV-NO-MACRO-PART-ENTITIES",
        "SilentMaterialChangeSmell",
        "OrphanBatchSmell",
        "ProvenanceDriftSmell",
    ]
    missing = [token for token in required_tokens if token not in text]
    if missing:
        return {
            "status": "fail",
            "message": "missing materials guardrail declaration(s): {}".format(",".join(missing)),
        }

    return {"status": "pass", "message": "materials guardrail declarations present"}
