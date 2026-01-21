--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None (policy docs only).
GAME:
- Uses capability schema for intent gating.
SCHEMA:
- Canonical capability taxonomy and denial semantics.
TOOLS:
- Capability audit and inspection tooling.
FORBIDDEN:
- No runtime logic in schema docs.
DEPENDENCIES:
- Engine -> none (schema only).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# Capabilities Schema (OMNI0)

This folder defines the taxonomy of capabilities and explicit denials.

See:
- `SPEC_CAPABILITY_TAXONOMY.md`
- `SPEC_NEGATIVE_CAPABILITIES.md`
