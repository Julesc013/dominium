Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Repository Inventory Summary

Machine-readable inventory: `docs/audit/INVENTORY_MACHINE.json`  
Test coverage inventory: `docs/audit/TEST_COVERAGE_MATRIX.md`

## Code subsystems (source roots)

- `engine` — `docs/engine/README.md`
- `game` — `docs/game/README.md`
- `client` — `docs/app/README.md`
- `server` — `docs/app/README.md`
- `launcher` — `docs/app/README.md`
- `setup` — `docs/app/README.md`
- `tools` — `docs/tools/TOOLING_OVERVIEW.md`
- `libs` — `docs/architecture/PROJECT_LIBRARIES.md`
- `app` — `docs/app/`
- `shared_ui_win32` — `docs/ui/`
- `sdk` — `docs/`

## Data domains (`data/` top-level)

Count: 14

- `archive`
- `capabilities`
- `compat`
- `defaults`
- `law`
- `logs`
- `modules`
- `packs`
- `profiles`
- `registries`
- `replays`
- `standards`
- `world`
- `worldgen`

## Pack families (`data/packs`)

Count: 59 pack directories. Family prefixes observed:

- `org.dominium.base.*`
- `org.dominium.core.*`
- `org.dominium.epistemics.*`
- `org.dominium.examples.*`
- `org.dominium.lib.*`
- `org.dominium.realities.*`
- `org.dominium.worldgen.*`

Pack validation status is captured in `docs/audit/PACK_AUDIT.txt`.

## Tooling surfaces

Top-level tool directories under `tools/`: 93  
Canonical tool inventory paths are recorded in `docs/audit/INVENTORY_MACHINE.json`.

## Schemas

`.schema` files under `schema/`: 154  
Governance: `schema/SCHEMA_VERSIONING.md`, `schema/SCHEMA_MIGRATION.md`, `schema/SCHEMA_VALIDATION.md`.

## Tests

CTest-discoverable tests: 309  
Coverage summary by prefix is in `docs/audit/TEST_COVERAGE_MATRIX.md`.

## CI / Build / Distribution paths

- CI: `ci/`, `scripts/ci/`, `.github/workflows/`
- Build: `build/`, `out/build/`, `cmake/`, `CMakePresets.json`, `CMakeLists.txt`
- Distribution: `dist/`, `updates/`, `docs/distribution/`, `docs/build/`
