# Authority and Entitlements (TESTX3)

Status: binding.
Scope: authority profiles, entitlements, and refusal semantics.

## Core invariants
- INVARIANT: AUTH3-AUTH-001 — Authority gates actions only, never visibility.
- INVARIANT: AUTH3-ENT-002 — Entitlements gate issuance of authority profiles only.
- INVARIANT: AUTH3-UPGRADE-007 — Authority changes do not mutate world state.

## Definitions
Authority:
- governs WHAT actions may occur
- never gates visibility
- never alters simulation logic or determinism

Entitlements:
- govern WHICH authority profiles may be issued
- are evaluated by launcher/platform/cloud only
- are not checked by engine/game

## Authority profiles (minimum set)
- base_free
- tourist
- full_player
- service_scoped
- admin

Profiles are closed-world and versioned in code and schema.

## Tokens and validation
- Authority tokens are opaque to engine/game.
- Tokens are validated server-side.
- Tokens are signed in production; tests use deterministic checksums only.
- Absence of authority results in explicit refusal, never silent fallback.

## Refusal semantics
When authority is missing or insufficient:
- action is refused
- refusal reason is logged
- no state mutation occurs
- determinism is preserved

## Cross-references
- `docs/arch/DEMO_AND_TOURIST_MODEL.md`
- `docs/arch/UPGRADE_AND_CONVERSION.md`
- `schema/authority/SPEC_AUTHORITY_LAYERS.md`
