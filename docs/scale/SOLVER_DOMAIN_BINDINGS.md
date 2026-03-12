Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to Domain/Contract registry schemas v1.0.0 and solver registry adapter schema v1.0.0.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Solver Domain Bindings

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Purpose
Define structural requirements for binding solver rows to domain and contract rows.

## Required Solver Binding Fields
Each solver record must declare:
- `domain_ids`
- `contract_ids`
- `transition_support`
- `resolution_tags`
- `cost_class`
- `refusal_codes`

## Collapse/Expand Discipline
- Collapse/expand requests must be checked against `transition_support`.
- If transition support is missing for a requested direction, refuse with `refusal.contract_violation`.
- No implicit transition support is allowed.

## Structural, Non-Semantic Rule
Binding checks do not alter solver math.  
These checks only assert that a selected solver is structurally legal for the requested domain/contract transition.

## Determinism
- Solver binding validation must be deterministic.
- Validation output ordering and refusal formatting must be deterministic.

## TODO
- Add compatibility matrix policy for solver upgrades across domain contract versions.
- Add explicit multi-solver arbitration contract for future prompts.

## Cross-References
- `docs/scale/DOMAIN_MODEL.md`
- `docs/scale/CONTRACTS_AND_CONSERVATION.md`
- `schema/scale/solver_registry_extension.schema`
