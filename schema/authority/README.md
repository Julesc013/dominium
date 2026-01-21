--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None (policy docs only).
GAME:
- Uses authority schema for capability evaluation and law gating.
SCHEMA:
- Canonical authority layers and omnipotence constraints.
TOOLS:
- Audit and inspection tooling for authority decisions.
FORBIDDEN:
- No runtime logic in schema docs.
DEPENDENCIES:
- Engine -> none (schema only).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# Authority Schema (OMNI0)

This folder defines the authority and capability model used to gate actions,
observation, overrides, and history changes.

See:
- `SPEC_AUTHORITY_LAYERS.md`
- `SPEC_CAPABILITY_DOMAINS.md`
- `SPEC_OMNIPOTENCE.md`
