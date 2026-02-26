Status: CANONICAL
Last Reviewed: 2026-02-26
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: MAT-0 materials ontology constitution
Binding Sources: docs/canon/constitution_v1.md, docs/canon/glossary_v1.md

# Materials Constitution

This document freezes the constitutional ontology for materials and production substrate work.

## 1) Material

- A **Material** is a ledger-tracked quantity with dimensional properties.
- Material representations:
  - macro stocks (canonical global truth),
  - meso stocks at logistics nodes,
  - micro instantiations only in active ROI.
- Materials are quantities and properties; they are not automatically entities.

## 2) Part

- A **Part** is a concrete assembly node constructed from materials.
- Part representation:
  - explicit micro part assemblies in ROI,
  - macro aggregated stock + provenance outside ROI.
- Each part must reference:
  - `parent_batch_id`
  - `assembly_graph_node_id`

## 3) Assembly Graph (AG)

- The **Assembly Graph** is a deterministic, schema-driven structural composition graph of parts.
- No implicit part creation is allowed.
- Graph mutation is process-driven only.

## 4) Batch

- A **Batch** is the canonical provenance unit for produced material and produced parts.
- Each batch includes:
  - source `process_id`,
  - input batch references,
  - timestamp tick,
  - quality and defect distribution payloads.
- Batches are the basis for recall, defect propagation, and reenactment continuity.

## 5) Commitment

- A **Commitment** is a scheduled obligation for:
  - production,
  - shipment,
  - construction,
  - maintenance.
- Commitments are canonical artifacts and must exist before policy-required macro state changes.

## 6) Provenance

- All material quantity and part state changes must be traceable through event logs and batch lineage.
- Provenance artifacts must remain compactable without breaking invariant continuity.

## 7) Collapse and Expand Rules

- Collapse must preserve:
  - total material quantities,
  - conservation ledger invariants,
  - defect and quality distributions.
- Expand must:
  - instantiate micro parts consistent with macro stocks,
  - assign deterministic IDs,
  - preserve provenance linkage,
  - preserve epistemic policy (no forbidden detail leak).

## 8) Nothing-Just-Happens Guarantee

- Every macro material change must originate from:
  - deterministic process execution,
  - a commitment where required by policy,
  - and/or explicit exception ledger accounting.
- Silent macro state edits are forbidden.

