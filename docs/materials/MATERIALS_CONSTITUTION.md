Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Materials Constitution

## Purpose
Define the authoritative ontology and constitutional guarantees for materials, parts, assemblies, provenance, commitments, and collapse/expand behavior before material-domain solver implementation.

## Scope Constraints
- This constitution does not implement solvers.
- This constitution does not introduce crafting gameplay systems.
- This constitution does not alter RS-2 conservation semantics.
- This constitution does not permit nondeterministic mutation paths.

## 1) Material
A Material is a ledger-tracked quantity with dimensional properties.

Material representations:
- macro stocks: canonical aggregate truth for authoritative accounting
- meso stocks: node-scoped logistics/accounting representation
- micro instantiations: explicit local realization inside active ROI only

Constitutional rule:
- Materials are not automatically entities; entity realization is tier- and process-dependent.

## 2) Part
A Part is a concrete assembly node constructed from materials.

Part representations:
- micro: explicit instantiated part in ROI
- macro: aggregated stock plus provenance references

Part identity anchors:
- `parent_batch_id`
- `assembly_graph_node_id`

## 3) Assembly Graph (AG)
The Assembly Graph is the deterministic, schema-driven structural composition tree of parts.

Constitutional rules:
- no implicit parts
- no runtime heuristic insertion of graph nodes
- all AG mutations are process-mediated and auditable

## 4) Batch
A Batch is the provenance unit for produced material and produced parts.

Required batch lineage payload:
- source `process_id`
- input batch references
- authoritative timestamp `tick`
- quality/defect distribution summary

Batch lineage supports:
- recall/containment workflows
- defect propagation analysis
- deterministic reenactment

## 5) Commitment
A Commitment is a scheduled obligation artifact for:
- production
- shipment
- construction
- maintenance

Constitutional rule:
- commitments must exist before macro material state changes are applied.
- commitments are canonical artifacts, not UI-only planning hints.

## 6) Provenance
All material changes must be traceable through deterministic event logs and batch lineage links.

Constitutional rules:
- every authoritative material delta must resolve to process + event + lineage context
- provenance may be compacted only when invariant continuity is preserved
- provenance artifacts remain replay/audit compatible after compaction

## 7) Collapse and Expand Rules
Collapse must:
- preserve total material quantities
- preserve ledger invariants
- preserve quality/defect distributions

Expand must:
- instantiate micro parts consistent with macro stocks
- assign deterministic IDs
- preserve provenance linkage
- avoid leaking epistemically forbidden detail

Cross-tier rule:
- collapse/expand behavior must remain consistent with RS-4 transition governance and ED-4 epistemic invariance.

## 8) Nothing-Just-Happens Guarantee
All macro material changes must originate from exactly one lawful path:
- a Process execution
- a Commitment execution step
- an explicit exception-ledger entry

Forbidden:
- silent state edits
- renderer/tool side mutation of truth
- out-of-band stock mutation without auditable causal artifact

## Constitutional Alignment
- A1 Determinism is primary.
- A2 Process-only mutation.
- A6 Provenance is mandatory.
- A7 Observer/Renderer/Truth separation.
- A9 Pack-driven integration for optional material capability surfaces.
