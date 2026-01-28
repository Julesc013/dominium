# Anti-Cheat as Law (OMNI0)

Status: binding.
Scope: integrity and anti-cheat expressed through capability law.

## Purpose
Define anti-cheat as law, not code exceptions. Cheat tools and admin tools are
the same intents, gated by capabilities, and fully auditable.

## Invariants
- Anti-cheat is law-gated, not hard-coded exceptions.
- Tool and admin intents require explicit capabilities.
- Overrides are audited and effect-driven.

## Anti-Cheat Model
- Integrity is an authority layer (INTEGRITY).
- Client admission, tool usage, and modified client policy are law targets.
- Denials such as DENY_MODIFIED_CLIENTS and DENY_EXTERNAL_TOOLS are explicit.
- Absence of capability is not a denial; law must refuse explicitly.

## Tools and Cheats as Capabilities
The following are intents that require explicit capabilities and law targets:
- console commands
- freecam
- teleport / forced travel
- spawn or destroy subjects
- terrain edits
- inspect hidden state

Anti-cheat is law that refuses these intents for most actors.

## Overrides and Audit
Any override (for testing or investigation) MUST:
- emit explicit effects,
- include capability evidence,
- record a full audit trail.

## Forbidden assumptions
- Cheats can be blocked by hidden code paths instead of law.
- Admin tools may bypass audit.

## Dependencies
- Authority layers: `schema/authority/SPEC_AUTHORITY_LAYERS.md`
- Law kernel: `schema/law/SPEC_LAW_KERNEL.md`

## See also
- `schema/authority/SPEC_AUTHORITY_LAYERS.md`
- `schema/capabilities/SPEC_NEGATIVE_CAPABILITIES.md`
- `schema/law/SPEC_LAW_KERNEL.md`
