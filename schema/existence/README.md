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

See:
- `SPEC_EXISTENCE_STATES.md`
- `SPEC_LIFECYCLE_TRANSITIONS.md`
- `SPEC_REFINEMENT_RELATION.md`
