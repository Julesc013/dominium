# SPEC_EXISTENCE_STATES (EXIST0)

Schema ID: EXISTENCE_STATES
Schema Version: 1.0.0
Status: binding.
Scope: canonical existence states for all entities, domains, and worlds.

## Purpose
Define explicit, universal existence states so nothing half-exists, pops into
existence, or disappears without an effect.

## Orthogonality
Existence is orthogonal to:
- Fidelity (macro vs micro representation)
- Authority (authoritative vs derived)

An object may be LATENT and authoritative, or REALIZED and derived.

## Canonical States
### NONEXISTENT
- Cannot be referenced.
- Cannot be refined.
- No provenance.

### DECLARED
- Exists conceptually (contracts, aggregates, history).
- No spatial presence yet.
- May transition to LATENT.

### LATENT
- Exists with minimal state (macro-only representation).
- May persist indefinitely.
- Refinement optional and contract-driven.

### REFINABLE
- Guaranteed to refine deterministically.
- Refinement contract exists and is satisfiable.
- May be visited if reachable.

### REALIZED
- Fully instantiated at micro level.
- Subject to budgets and interest.
- May collapse back to LATENT.

### ARCHIVED
- Frozen and read-only.
- May be replayed or forked.
- Cannot mutate unless explicitly forked.

## Invariants (Absolute)
- Existence must never be inferred.
- Absence is a valid state.
- Refinement does not fabricate history.
- Archival preserves truth.
- Collapse must preserve invariants.
- Nothing transitions without cause.

## References
- `schema/existence/SPEC_LIFECYCLE_TRANSITIONS.md`
- `docs/architecture/EXISTENCE_AND_REALITY.md`
