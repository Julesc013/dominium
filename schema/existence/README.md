--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None (policy docs only).
GAME:
- Uses existence schema for law gating and lifecycle effects.
SCHEMA:
- Canonical existence states, transitions, and refinement relations.
TOOLS:
- Validation and inspection tooling for existence metadata.
FORBIDDEN:
- No runtime logic in schema docs.
DEPENDENCIES:
- Engine -> none (schema only).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# Existence Schema (EXIST0)

This folder defines the canonical existence model used by all domains,
entities, and worlds.

Scope: existence states, lifecycle transitions, refinement, and archival.

## Invariants
- Existence is explicit; no implicit creation or erasure.
- Refinement and collapse are contract-driven.
- Archival history is immutable unless forked.

## Forbidden assumptions
- Existence can be inferred without explicit state.
- Refinement can fabricate provenance.

## Dependencies
- `docs/architecture/REALITY_LAYER.md`
- `docs/architecture/SPACE_TIME_EXISTENCE.md`

See:
- `SPEC_EXISTENCE_STATES.md`
- `SPEC_LIFECYCLE_TRANSITIONS.md`
- `SPEC_REFINEMENT_RELATION.md`
- `SPEC_REFINEMENT_CONTRACTS.md`
- `SPEC_COLLAPSE_CONTRACTS.md`
- `SPEC_REFINEMENT_DENIAL.md`
- `SPEC_REFINEMENT_SEEDS.md`
- `SPEC_ARCHIVAL_STATES.md`
- `SPEC_FREEZE_SEMANTICS.md`
- `SPEC_FORKING_RULES.md`
- `SPEC_DESTRUCTION_RULES.md`

Reality layer:
- `docs/architecture/REALITY_LAYER.md`
- `docs/architecture/SPACE_TIME_EXISTENCE.md`
- `docs/architecture/VISITABILITY_AND_REFINEMENT.md`
