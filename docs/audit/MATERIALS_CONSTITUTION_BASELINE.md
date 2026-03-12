Status: DERIVED
Last Reviewed: 2026-02-27
Version: 1.0.0
Scope: MAT-0 constitutional baseline for material ontology and guardrails.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Materials Constitution Baseline

## 1) Ontology Definitions
MAT-0 establishes and freezes:
- Material as ledger-tracked quantity across macro/meso/micro representations.
- Part as assembly node with `parent_batch_id` and `assembly_graph_node_id`.
- Assembly Graph (AG) as deterministic, schema-driven structural composition with no implicit parts.
- Batch as provenance unit with process source, input lineage, tick, and quality/defect distribution.
- Commitment as canonical scheduled obligation (production/shipment/construction/maintenance).
- Provenance as mandatory process/event/batch traceability with compactable continuity.
- Collapse/expand constitutional behavior preserving quantities, distributions, provenance, and epistemic boundaries.
- Nothing-just-happens guarantee: all macro changes require process, commitment, or exception-ledger cause.

Primary documents:
- `docs/materials/MATERIALS_CONSTITUTION.md`
- `docs/materials/PROVENANCE_AND_COMMITMENTS.md`
- `docs/materials/TIERED_MATERIAL_REPRESENTATION.md`
- `docs/materials/FAILURE_AND_MAINTENANCE_MODEL.md`
- `docs/materials/MATERIAL_INVARIANTS.md`
- `docs/materials/GUARDRAIL_DECLARATIONS.md`

## 2) Tier Mapping Rules
- Macro stores aggregate stock and quality vectors only (no per-part entities).
- Meso stores logistics-node inventories, batch refs, and shipment commitments.
- Micro stores explicit assemblies and part-local wear/defect/geometry in ROI only.
- Micro entities are ephemeral and derivable from macro + provenance; collapse/expand remains deterministic and replay-safe.

## 3) Provenance And Commitment Guarantees
- Material-changing processes emit deterministic event artifacts with input/output batch references and ledger deltas.
- Commitment lifecycle is canonical: `planned -> scheduled -> executing -> completed|failed`.
- Reenactment contract supports deterministic meso reconstruction and optional ROI micro reconstruction.
- Compaction preserves lineage integrity, invariant continuity, and hash-chain continuity.

## 4) Collapse/Expand Invariants
Defined invariants include:
- preservation of `sum(material.mass_energy_total)` across collapse/expand boundaries
- acyclic, traceable batch lineage
- round-trip stability (`Expand -> Collapse -> Expand`) for stock + distributions within tolerance
- no epistemic gain via refinement
- no silent material mutation outside process boundaries

Cross-contract links:
- RS-2: `docs/reality/CONSERVATION_AND_EXCEPTIONS.md`
- RS-4: `docs/reality/TIER_TAXONOMY_AND_TRANSITIONS.md`
- ED-4: `docs/epistemics/LOD_EPISTEMIC_INVARIANCE.md`

## 5) Guardrail Declarations
### RepoX rules
- `INV-MATERIAL-MUTATION-PROCESS-ONLY`
- `INV-PROVENANCE-REQUIRED`
- `INV-BATCH-LINEAGE-ACYCLIC`
- `INV-NO-MACRO-PART-ENTITIES`

### AuditX analyzers
- `SilentMaterialChangeSmell`
- `OrphanBatchSmell`
- `ProvenanceDriftSmell`

### Required future tests
- `test_batch_lineage_integrity`
- `test_collapse_expand_material_conservation`
- `test_provenance_compaction_integrity`
- `test_commitment_event_required_for_macro_change`
- `test_no_silent_material_mutation`

## 6) Extension Points For MAT-1..MAT-10
1. MAT-1: process surfaces and schema anchors for material, batch, and commitment artifacts.
2. MAT-2: deterministic batch lineage execution and defect propagation kernels.
3. MAT-3: assembly-graph materialization and deterministic part identity assignment.
4. MAT-4: macro<->meso logistics execution with commitment scheduling.
5. MAT-5: ROI micro expand/collapse implementation with replay/hash checks.
6. MAT-6: compaction and reenactment tooling with checkpoint continuity proofs.
7. MAT-7: maintenance backlog execution and deterministic failure integration.
8. MAT-8: RepoX/AuditX rule implementation for declared material guardrails.
9. MAT-9: TestX suite implementation for declared material invariants.
10. MAT-10: multiplayer/SRZ proof envelope integration for material provenance and commitments.

## 7) Gate Execution Snapshot (2026-02-27)
1. RepoX PASS
   - command: `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, findings=1 warn (`INV-AUDITX-REPORT-STRUCTURE`)
2. AuditX run
   - command: `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, findings=1628 (warn-level scan findings present)
3. TestX PASS (documentation + guard presence)
   - command: `py -3 tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.materials.guardrail_declarations_present`
   - result: `status=pass`, selected_tests=1
4. strict build PASS
   - command: `py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.mat0 --cache on --format json`
   - result: `result=complete` (build + validation complete)

## 8) Notes
- A broader optional strict negative-invariant smoke test currently contains a pre-existing unrelated failure (`INV-REPRESENTATION-RENDER-ONLY`) and is outside MAT-0 scope.
