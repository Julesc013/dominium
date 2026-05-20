Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none

# DEPENDENCY_DIRECTION_01

Result: PARTIAL

## Why

Dominium's canonical roots need enforceable dependency direction so `engine/`,
`runtime/`, `game/`, `apps/`, `contracts/`, `content/`, `tools/`, `tests`,
`release/`, and `archive/` do not decay after cleanup.

## Changed

- Added `contracts/repo/dependency_directions.contract.toml`.
- Added `contracts/repo/dependency_direction.schema.json`.
- Added `contracts/repo/dependency_direction_exceptions.toml`.
- Added `tools/validators/repo/check_dependency_directions.py`.
- Added dependency-direction docs and fixtures.
- Registered dependency-direction surfaces in the public surface registry.
- Added task evidence under `.aide/reports/DEPENDENCY-DIRECTION-01-*`.

## Proof

- New validator compiles.
- Contract, exception file, schema, and fixture parses pass.
- Public surface validator passes with 30 surfaces.
- ABI validator passes with 0 errors and existing 2,851 warnings.
- Strict repo/root/distribution/component validators pass.
- Docs/build/UI/ABI supplemental checks pass.
- Fast strict passes: 32/32 commands in 334.907 seconds.

## Known Debt

The new validator is intentionally strict and exposes current dependency debt:

- 358 high-confidence violations.
- 38 warnings.
- 0 active exceptions.
- 0 broad exceptions.

The main violation class is active Python imports from `apps/`, `engine/`,
`game/`, and `runtime/` into `tools/`. These are not hidden or marked clean.

## Next

`COMMAND-SURFACE-01`

Feature work remains blocked until Foundation Lock closes.
