# Upgrade and Conversion (TESTX3)

Status: binding.
Scope: authority upgrade/downgrade and save tagging.

## Core invariants
- INVARIANT: AUTH3-UPGRADE-007 — Authority changes do not mutate world state.
- INVARIANT: AUTH3-SAVE-008 — Saves are tagged with authority scope.

## Upgrade rules
- Authority upgrades are instant and clean.
- Upgrades do not mutate world state.
- Refusals are explicit and logged.

## Downgrade rules
- Authority downgrades do not corrupt state.
- Downgrades do not invalidate replays.
- Downgrades are explicit and logged.

## Saves and replays
- Saves are tagged with authority scope.
- base_free and tourist saves are non-authoritative.
- full_player saves are authoritative.
- Replays are always valid across authority changes.

## Cross-references
- `docs/architecture/AUTHORITY_AND_ENTITLEMENTS.md`
