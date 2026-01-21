--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None (policy docs only).
GAME:
- Uses authority schema for capability sets, profiles, and law integration.
SCHEMA:
- Canonical authority layers, capability scoping, and omnipotence definitions.
TOOLS:
- Audit, inspection, and explanation tooling consume authority data.
FORBIDDEN:
- No runtime logic in schema docs.
DEPENDENCIES:
- Engine -> none (schema only).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# Authority Schema (OMNI0)

This folder defines the canonical authority model used across spectator,
competitive, anarchy, and omnipotent control without modes or hard-coded
admin flags.

Scope: authority layers, capability domains, and omnipotence definitions.

## Invariants
- Capabilities are additive and scoped.
- Law gates every authoritative action.
- Omnipotence is capability union, not bypass.

## Forbidden assumptions
- "Admin" flags replace law gating.
- Authority implies unsandboxed mutation.

## Dependencies
- `docs/arch/AUTHORITY_AND_OMNIPOTENCE.md`
- `docs/arch/REALITY_LAYER.md`

Specs:
- `SPEC_AUTHORITY_LAYERS.md`
- `SPEC_CAPABILITY_DOMAINS.md`
- `SPEC_OMNIPOTENCE.md`
- `SPEC_TOOL_AUTHORITY.md`

Related:
- Capability taxonomy: `schema/capabilities/README.md`
- Law kernel: `schema/law/SPEC_LAW_KERNEL.md`
- Authority architecture: `docs/arch/AUTHORITY_AND_OMNIPOTENCE.md`

Reality layer:
- `docs/arch/REALITY_LAYER.md`
- `docs/arch/AUTHORITY_IN_REALITY.md`
