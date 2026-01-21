--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None (policy docs only).
GAME:
- Uses tool schemas to define ToolIntent and tool capability sets.
SCHEMA:
- Canonical ToolIntent, tool capability, and scoping formats.
TOOLS:
- Inspection and dev tools consume these schemas for gating and audit.
FORBIDDEN:
- No runtime logic in schema docs.
DEPENDENCIES:
- Engine -> none (schema only).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# Tools Schema (OMNI1)

This folder defines how developer tools and cheat-like features are modeled
as law-gated ToolIntents with explicit capabilities and audit trails.

Specs:
- `SPEC_TOOL_INTENTS.md`
- `SPEC_TOOL_CAPABILITIES.md`
- `SPEC_TOOL_SCOPING.md`

Related:
- Authority integration: `schema/authority/SPEC_TOOL_AUTHORITY.md`
- Law kernel: `schema/law/SPEC_LAW_KERNEL.md`
