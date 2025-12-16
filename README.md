# DOMINIUM & DOMINO

**Domino** is the deterministic, fixed-point simulation engine (C89/C90).  
**Dominium** is the product layer (C++98) that hosts runtime/UI/platform integration on top of Domino.

## Architecture (high level)
- Layers: Domino engine (`source/domino/`, `include/domino/**`) and Dominium products (`source/dominium/`, `include/dominium/**`).
- Determinism: integer ticks, fixed-point math, canonical ordering, replay, and world hashing (`docs/SPEC_DETERMINISM.md`).
- Dependency boundaries: engine must not depend on the product layer; see `docs/ARCHITECTURE.md` and `docs/DEPENDENCIES.md`.

## Supported platforms (high level)
- Windows baseline: `DOM_PLATFORM=win32` and `DOM_PLATFORM=win32_headless`.
- Optional host backends (build-gated): Linux (`posix_x11`, `posix_wayland`), macOS (`cocoa`).
- Canonical configurations and prerequisites: `docs/BUILD_MATRIX.md`, `docs/SETUP_WINDOWS.md`, `docs/SETUP_LINUX.md`, `docs/SETUP_MACOS.md`.

## Build overview
- Build system: CMake (presets supported).
- Build + test instructions: `docs/BUILDING.md`.
- Smoke/verification contract: `docs/SPEC_SMOKE_TESTS.md`.

## Documentation map
Start here:
- Documentation index: `docs/README.md`
- Directory/layout contract: `docs/DIRECTORY_CONTEXT.md`
- Architecture and layering: `docs/ARCHITECTURE.md` (see also `docs/OVERVIEW_ARCHITECTURE.md`)
- API contracts: `docs/CONTRACTS.md`
- Commenting/coding style: `docs/STYLE.md`
- Language/toolchain policy: `docs/LANGUAGE_POLICY.md`

Key specs:
- Determinism and regressions: `docs/SPEC_DETERMINISM.md`, `docs/DETERMINISM_REGRESSION_RULES.md`
- SIM pipeline: `docs/SPEC_SIM_SCHEDULER.md`, `docs/SPEC_ACTIONS.md`
- Serialization ABI and formats: `docs/SPEC_CONTAINER_TLV.md`, `docs/DATA_FORMATS.md`

## Repository map
Key roots:
- `include/` – public headers (`include/domino/**`, `include/dominium/**`)
- `source/domino/` – engine implementation
- `source/dominium/` – products (launcher, game, setup, tools)
- `docs/` – specs and policy docs
- `data/` – in-tree content sources
- `repo/` – runtime repo layout under `DOMINIUM_HOME`

## Contributing
See `CONTRIBUTING.md`.

## License
See `LICENSE`.
