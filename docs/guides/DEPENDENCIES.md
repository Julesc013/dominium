Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Dependencies (Allowed / Forbidden)





This document defines the enforceable dependency directions between current


top-level components. It complements:


- Layout contract: `docs/architecture/DIRECTORY_CONTEXT.md`


- Language/determinism constraints: `docs/specs/SPEC_LANGUAGE_BASELINES.md`,


  `docs/specs/SPEC_DETERMINISM.md`





## Allowed dependency graph (high level)


- `engine/` → (no top-level product directories)


- `game/` → `engine/`


- `client/`, `server/` → `engine/` + `game/`


- `launcher/` → `engine/` (public headers) + `libs/contracts`


- `setup/` → `libs/contracts`


- `tools/` → `libs/contracts` and select engine public APIs (e.g., `data_validate`)


- `libs/` → leaf (no engine/game/launcher/setup/tools dependencies)


- `schema/` → data-only (no code dependencies)





## Forbidden dependency edges (must not exist)


- `engine/` → `game/`, `client/`, `server/`, `launcher/`, `setup/`, `tools/`, `libs/`


- `game/` → `launcher/`, `setup/`, `tools/`, `libs/`


- `client/`, `server/` → `launcher/`, `setup/`, `tools/`, `libs/`


- `launcher/` → `game/`, `setup/`, `tools/`


- `setup/` → `engine/`, `game/`, `launcher/`, `tools/`


- `tools/` → `game/`, `launcher/`, `setup/`


- Any circular dependency between top-level directories





## Public header rules


Public header boundaries and ABI rules are defined in `docs/specs/CONTRACTS.md`.


Include rules are enforced by `tools/ci/arch_checks.py`.





## Determinism boundary


- Authoritative code must not use wall-clock time, non-deterministic RNG, or


  platform APIs. See `docs/specs/SPEC_DETERMINISM.md`.





## Enforcement


- CMake boundary checks: root `CMakeLists.txt` uses `dom_assert_no_link(...)`.


- Include/scan checks: `tools/ci/arch_checks.py` (ARCH-DEP-001/002, ARCH-INC-001/002).





## See also


- `docs/architecture/CANONICAL_SYSTEM_MAP.md`


- `docs/architecture/INVARIANTS.md`
