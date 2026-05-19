Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Semantic Contract Baseline

## Baseline v1 Contracts
- `contract.worldgen.refinement.v1`
- `contract.overlay.merge.v1`
- `contract.logic.eval.v1`
- `contract.proc.capsule.v1`
- `contract.sys.collapse.v1`
- `contract.geo.metric.v1`
- `contract.geo.projection.v1`
- `contract.geo.partition.v1`
- `contract.appshell.lifecycle.v1`

## Guaranteed Invariants
- semantic meaning changes cannot drift silently
- new universes pin an immutable semantic contract bundle at creation
- replay comparison refuses mismatched contract bundles without explicit migration invocation
- old universes remain on pinned `v1` behavior semantics

## Migration Policy Summary
- semantic contract version increments are explicit
- CompatX migration descriptors and tools are required before accepting semantic transitions
- absent migration support yields deterministic refusal, not best-effort coercion

## No Behavior Change Confirmation
- this baseline adds metadata, proofs, and enforcement only
- worldgen, overlay, logic, GEO, SYS, PROC, and app-shell algorithms are unchanged
