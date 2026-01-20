# SPEC_REFINEMENT_RELATION (EXIST0)

Schema ID: EXISTENCE_REFINEMENT
Schema Version: 1.0.0
Status: binding.
Scope: refinement relation between LATENT, REFINABLE, and REALIZED.

## Purpose
Define how macro-only entities can refine to micro detail without fabricating
history, and how realized detail can collapse back to latent form.

## Refinement Contract (EXIST1 hook)
Refinement is allowed only when a deterministic contract exists. The contract
binds:
- subject_id (or domain scope)
- seed/provenance reference
- domain volume and boundaries
- refinement rules and determinism class
- required inputs (immutable history, authoritative state)
- output guarantees (what REALIZED must contain)

Refinement contracts are defined by EXIST1; EXIST0 only requires they exist.

## Refinement Relation
- LATENT: may or may not have a contract.
- REFINABLE: a contract exists and is satisfiable.
- REALIZED: contract has been applied; micro detail instantiated.

## Determinism and History
- Refinement must be deterministic given the same contract and history.
- Refinement does not fabricate events or provenance.
- Collapse preserves authoritative invariants and provenance references.

## Domain Integration
- Refinement respects DOMAIN volumes and ownership.
- Domain boundaries are stable across refinement and collapse.
- Cross-domain refinement is forbidden unless explicitly contracted.

## Budget and Interest Integration
- REALIZED is subject to budgets and interest gating.
- LATENT can persist indefinitely without simulation cost.
- Refinement must not depend on wall-clock or nondeterministic signals.

## References
- `schema/existence/SPEC_EXISTENCE_STATES.md`
- `schema/existence/SPEC_LIFECYCLE_TRANSITIONS.md`
