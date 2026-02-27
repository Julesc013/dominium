Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.

# Materials Guardrail Declarations

## Purpose
Declare MAT-0 required future test coverage and guardrail identifiers for RepoX and AuditX.

## TestX Declarations (Required Future Tests)
- `test_batch_lineage_integrity`
- `test_collapse_expand_material_conservation`
- `test_provenance_compaction_integrity`
- `test_commitment_event_required_for_macro_change`
- `test_no_silent_material_mutation`

## RepoX Rule Declarations
- `INV-MATERIAL-MUTATION-PROCESS-ONLY`
  - Authoritative material mutation must occur only through Process commit boundaries.
- `INV-PROVENANCE-REQUIRED`
  - Material-changing operations must emit traceable provenance links.
- `INV-BATCH-LINEAGE-ACYCLIC`
  - Batch lineage graph must remain acyclic and traceable.
- `INV-NO-MACRO-PART-ENTITIES`
  - Macro tier must not persist per-part entities.

## AuditX Analyzer Declarations
- `SilentMaterialChangeSmell`
- `OrphanBatchSmell`
- `ProvenanceDriftSmell`

## MAT-0 Status
- These declarations are constitutional commitments in MAT-0.
- Enforcement implementation and deeper runtime coverage are MAT-1..MAT-10 work.
