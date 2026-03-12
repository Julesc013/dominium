Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# BOM And Assembly Graph

## Purpose
Define deterministic, pack-driven Bill of Materials (BOM) and Assembly Graph (AG) contracts for MAT-3 blueprint compilation.

## Scope Constraints
- No crafting/inventory mechanics.
- No full manufacturing process-chain solver.
- No structural physics solver.
- No hardcoded Earth-specific structures.

## A) Bill Of Materials (BOM)
- BOM is an abstract requirement manifest for assembly realization.
- BOM contains deterministic material quantity requirements by material id/class.
- BOM may include abstract part-class counts (for bolts/beams/panels) without forcing micro instantiation.
- Optional tolerance stubs are allowed for future quality/fit validation.

Primary uses:
- planning and cost estimation
- logistics planning
- commitment planning before macro mutation

## B) Assembly Graph (AG)
- AG is a deterministic, schema-validated hierarchy of nodes and typed connections.
- Nodes represent parts, subassemblies, connectors, or site anchors.
- Edges represent connection tags only at MAT-3 (example: bolted, welded, riveted, press-fit, mortar).
- AG supports:
  - nested subassemblies
  - parameterized templates
  - deterministic instancing expansion for large repeated modules
- AG has no implicit nodes or hidden expansion behavior.

## C) Provenance And Commitments
Each AG node may declare:
- `node_id`
- planned batch inputs
- output part batch id (when produced)
- milestone commitment ids (optional)

Construction is process-bound:
- no construction state appears without commitment/event provenance
- node realization must be attributable to process execution (MAT-5 integration path)

## Determinism Rules
- Node and edge ordering is canonicalized before hash/compile artifacts.
- Parameter expansion order is deterministic.
- Artifact identity is derived from canonical payload hashes only.
- Missing registry references must refuse with deterministic refusal codes.

## Constitutional Alignment
- A1 Determinism is primary.
- A2 Process-only mutation.
- A6 Provenance is mandatory.
- A9 Pack-driven integration.
