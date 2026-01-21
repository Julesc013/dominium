--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None (policy docs only).
GAME:
- Uses capability taxonomy and sets for authority decisions.
SCHEMA:
- Canonical capability identifiers and denial semantics.
TOOLS:
- Audit and inspection tooling reads capability data.
FORBIDDEN:
- No runtime logic in schema docs.
DEPENDENCIES:
- Engine -> none (schema only).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# Capabilities Schema (OMNI0)

This folder defines the canonical capability vocabulary used by law-gated
authority across all profiles.

Specs:
- `SPEC_CAPABILITY_TAXONOMY.md`
- `SPEC_NEGATIVE_CAPABILITIES.md`

Related:
- Authority layers: `schema/authority/SPEC_AUTHORITY_LAYERS.md`
- Law kernel: `schema/law/SPEC_LAW_KERNEL.md`
