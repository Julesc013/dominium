Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Collapse Expand Solvers

## Solver Registry
- Solver metadata is defined in `data/registries/solver_registry.json`.
- Each solver record declares:
  - `solver_id`
  - `cost_class`
  - `resolution`
  - `guarantees`
  - `supports_transitions`
  - `numeric_bounds`
  - `refusal_codes`
- Solver identifiers are stable and append-only.

## Solver Guarantees, Cost, And Resolution
- `cost_class` declares deterministic budget profile expectations.
- `resolution` declares macro/micro/hybrid fidelity scope.
- `guarantees` enumerates invariants promised by the solver output.
- `numeric_bounds` declares bounded-error policy used by refusal checks.

## State Mapping Rules
- Collapse maps refined state into contract-preserving summaries.
- Expand maps summaries back into refined state only through declared solver mappings.
- Mapping must preserve conservation, contract invariants, and provenance references.
- Transition ordering is deterministic and auditable.

## Denied Expansion Semantics
- Expansion refusal is mandatory when:
  - requested solver is ineligible by conformance bundle
  - numeric bounds cannot be met
  - deterministic budget constraints would be violated
- Denial must emit stable refusal codes and audit-visible context.

## Dependencies
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
- `docs/architecture/REFUSAL_SEMANTICS.md`
- `docs/architecture/SCALING_MODEL.md`
