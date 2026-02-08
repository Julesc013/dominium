Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Complexity And Scale

## Hierarchical Assemblies
- Assemblies are the only artifact composition unit for items, machines, and structures.
- Parts and components are assemblies with explicit interface contracts.
- Assembly hierarchy remains data-defined; no special-case runtime item systems are allowed.

## Contracts, Ports, And Conformance Bundles
- Assembly interaction contracts are expressed through typed ports:
  - mechanical
  - electrical
  - fluid
  - thermal
  - signal
  - legal/ownership
- Conformance bundles declare tolerances, invariant checks, test vectors, and solver eligibility.
- Runtime refusal is mandatory when declared contracts cannot be satisfied.

## Multi-Scale Simulation Policy
- Scale handling is solver selection, not LOD substitution.
- Macro and micro views are contract-equivalent representations with explicit transition semantics.
- Solver choice is deterministic and bounded by declared cost class and resolution.

## Budgeted Determinism And Kraken Prevention
- Execution budgets are explicit and deterministic per region/artifact context.
- Solver expansion may be refused when contract bounds or budget constraints would be violated.
- Refusal outcomes are explicit, reproducible, and audit-visible.

## Dependencies
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
- `docs/architecture/REFINEMENT_CONTRACTS.md`
- `docs/architecture/INVARIANTS_AND_TOLERANCES.md`
