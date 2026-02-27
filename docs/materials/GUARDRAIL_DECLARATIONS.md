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

## MAT-2 Additions (Material Taxonomy)
### TestX Declarations
- `test_element_registry_valid`
- `test_compound_mass_fraction_sum`
- `test_mixture_mass_fraction_sum`
- `test_material_batch_creation_deterministic`
- `test_ledger_mass_tracking_by_material`

### RepoX Rule Declarations
- `INV-MATERIAL-DEFINITIONS-DATA-ONLY`
  - Elements, compounds, mixtures, and material classes must be declared in registries.
- `INV-NO-HARDCODED-ELEMENTS`
  - Runtime source must not embed fixed periodic-table element IDs.
- `INV-COMPOSITION-VALIDATED`
  - Composition and dimensional compatibility checks must run through deterministic validators.

### AuditX Analyzer Declarations
- `HardcodedPeriodicTableSmell`
- `MaterialMassDriftSmell`

## MAT-3 Additions (BOM + Assembly Graph + Blueprint Compile)
### TestX Declarations
- `test_blueprint_compile_deterministic`
- `test_bom_ag_schema_valid`
- `test_instancing_expansion_deterministic`
- `test_missing_part_class_refusal`
- `test_blueprint_visualization_render_model_hash_stable`

### RepoX Rule Declarations
- `INV-BLUEPRINTS-DATA-ONLY`
  - Blueprint templates and baseline structures must be defined in data packs/registries, not hardcoded in runtime source.
- `INV-DETERMINISTIC-BLUEPRINT-COMPILATION`
  - Blueprint compilation must produce canonical BOM/AG artifacts under deterministic ordering and instancing rules.
- `INV-NO-HARDCODED-STRUCTURES`
  - Runtime source must not embed fixed concrete structures that bypass blueprint registry flow.

### AuditX Analyzer Declarations
- `HardcodedBlueprintSmell`
- `NonDeterministicGraphOrderSmell`

## MAT-4 Additions (Logistics Graph + Manifests + Delivery Commitments)
### TestX Declarations
- `test_manifest_create_deterministic`
- `test_manifest_tick_delivery_deterministic`
- `test_loss_fraction_deterministic`
- `test_conservation_ledger_transfer_balanced`
- `test_budget_degrade_order_deterministic`
- `test_visual_overlay_render_model_hash_stable`

### RepoX Rule Declarations
- `INV-NO-SILENT-TRANSFER`
  - Logistics stock transfer must always be represented by manifest commitments/events and process commits.
- `INV-MANIFESTS-PROCESS-ONLY`
  - Manifest, shipment commitment, and node-inventory state mutation is process-runtime only.
- `INV-LOGISTICS-DETERMINISTIC-ROUTING`
  - Routing and manifest progression must use deterministic ordering/tie-breaks.

### AuditX Analyzer Declarations
- `SilentShipmentSmell`
- `NonDeterministicRoutingSmell`

## MAT-5 Additions (Construction + Installation + Provenance Events)
### TestX Declarations
- `test_project_create_deterministic`
- `test_step_scheduling_deterministic`
- `test_material_consumption_balanced`
- `test_insufficient_material_refusal`
- `test_provenance_events_deterministic`
- `test_visualization_render_model_hash_stable`
  - construction coverage implementation: `test_construction_visualization_render_model_hash_stable`
- `test_budget_parallelism_reduction_deterministic`

### RepoX Rule Declarations
- `INV-CONSTRUCTION-REQUIRES-COMMITMENTS`
  - Construction project and step progression must be commitment-linked before macro install state mutation.
- `INV-PROVENANCE-EVENTS-REQUIRED`
  - Construction/install mutation paths must emit deterministic provenance events with causal links.
- `INV-LEDGER-DEBIT-CREDIT-REQUIRED`
  - Construction material consumption and part-batch creation must include balanced ledger deltas.
- `INV-NO-SILENT-INSTALL`
  - Installed structure state cannot mutate outside canonical process runtime paths.

### AuditX Analyzer Declarations
- `SilentConstructionSmell`
- `MissingProvenanceSmell`

## MAT-0 Status
- These declarations are constitutional commitments in MAT-0.
- Enforcement implementation and deeper runtime coverage are MAT-1..MAT-10 work.
