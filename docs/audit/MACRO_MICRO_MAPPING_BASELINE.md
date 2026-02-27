Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, MAT-0, RS-2, RS-4, RS-5, ED-4.

# Macro Micro Mapping Baseline

## Scope
MAT-7 baseline introduces deterministic macro/micro part materialization with process-only mutation, ROI bounds, and invariant checks.

## Materialization Rules
- Macro canonical state:
  - `distribution_aggregates`
  - installed structure node completion state
- Micro derived state:
  - `micro_part_instances`
  - `materialization_states`
  - `materialization_reenactment_descriptors`
- Expansion process:
  - `process.materialize_structure_roi`
  - deterministic part ordering by `(ag_node_id, batch_id, index)`
  - deterministic IDs and seeds via canonical hash stream `"materialization"`
- Collapse process:
  - `process.dematerialize_structure_roi`
  - aggregates micro mass/defect/wear back into canonical distribution rows

## Invariant Preservation Guarantees
- Expand invariant:
  - `inv.transition.expand_materialization`
  - compares source aggregate mass vs generated micro mass
- Collapse invariant:
  - `inv.transition.collapse_materialization`
  - compares collapsed aggregate mass vs removed micro mass
- Strict path:
  - refusal `refusal.transition.invariant_violation`
- Non-strict drift path:
  - ledger exception `exception.numeric_error_budget`
- Budget enforcement:
  - refusal `refusal.materialization.budget_exceeded` in strict-budget mode
  - deterministic truncation otherwise

## Epistemic Safety Guarantees
- PerceivedModel remains macro-first; no direct micro-part channel is introduced.
- Inspection snapshots apply materialization-specific augmentation and diegetic redaction:
  - redact micro-part ID lists for diegetic materialization-state views
  - quantize distribution vectors
  - redact seed references in diegetic reenactment descriptor views

## Performance Constraints
- `materialization_max_micro_parts_per_roi` policy cap enforced in runtime.
- Overlay rendering for materialization is capped by deterministic `materialization_overlay_max_parts` ordering.
- Truncation metadata is emitted deterministically in process result metadata and overlay extensions.

## Reenactment Support
- Each micro part stores deterministic seed and parent lineage references.
- `materialization_reenactment_descriptors` persist:
  - structure ID
  - tick range
  - AG nodes and batches involved
  - stable seed reference hash

## Guardrails And Tests
- RepoX:
  - `INV-NO-GLOBAL-MICRO-PARTS`
  - `INV-MACRO-STOCK-CANONICAL`
  - `INV-MATERIALIZATION-DETERMINISTIC`
- AuditX:
  - `MicroEntityLeakSmell`
  - `CollapseDriftSmell`
- TestX:
  - `test_materialize_deterministic_ids`
  - `test_collapse_preserves_mass`
  - `test_expand_collapse_expand_stability`
  - `test_epistemic_no_leak_outside_roi`
  - `test_truncation_deterministic`
  - `test_reenactment_seed_reproducible`

## Extension Points
- MAT-8 reenactment playback:
  - consume `materialization_reenactment_descriptors` + provenance to reconstruct micro timelines
- MAT-9/10 deeper micro simulation:
  - add optional higher-fidelity micro state models while preserving MAT-7 collapse contracts
- Domain packs:
  - add domain-specific defect/wear aggregation models through registry-driven extensions

