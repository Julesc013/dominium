Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.

# Tiered Material Representation

## Purpose
Define authoritative material representation contracts across macro, meso, and micro tiers.

## Macro Tier
Macro representation is aggregate and canonical.

Macro stores:
- material quantities only (stock ledger channels)
- quality distributions as statistical vectors
- commitment totals and macro obligation state

Macro forbids:
- per-bolt or per-part entity persistence
- hidden micro-only state leakage

## Meso Tier
Meso representation is logistics-node scoped and deterministic.

Each logistics node maintains:
- inventory counts
- batch references
- shipment commitments

Meso role:
- bridge macro stock accounting to transport/transfer execution
- retain provenance continuity without requiring micro instantiation everywhere

## Micro Tier
Micro representation is explicit, local, and ROI-bound.

Micro stores:
- explicit part assemblies
- part-specific state (`wear`, defect flags, geometry)
- process-local maintenance/failure context

Micro existence rule:
- micro entities exist only in active ROI contexts.

## Cross-Tier Rules
1. Macro never stores per-part entities.
2. Micro entities are ephemeral and derivable from macro state + provenance lineage.
3. Expand derives micro state deterministically from macro/meso + batch/AG references.
4. Collapse reduces micro state back into macro/meso summaries without conservation or lineage drift.
5. Tier transitions must remain thread-count invariant and replay-equivalent.

## Determinism and Epistemic Safety
- Tier arbitration and transitions are deterministic and policy-driven.
- Micro refinement must not produce unauthorized information gain.
- Observation/lens filtering applies after truth derivation; rendering remains non-mutating.

## Constitutional Alignment
- A1 Determinism is primary.
- A2 Process-only mutation.
- A7 Observer/Renderer/Truth separation.
- E2 Deterministic ordering.
- E5 Thread-count invariance.
