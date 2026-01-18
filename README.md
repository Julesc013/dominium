# Dominium / Domino
Dominium is a deterministic simulation game runtime built on the Domino engine.

## What this project is (non-technical)
Dominium provides a deterministic simulation runtime and the surrounding product
stack needed to install, launch, and run it. It is designed so the same inputs
produce the same results across supported builds, enabling reproducible saves,
replays, and verification.

It is:
- a game runtime and toolchain (engine + game + launcher + setup + tools).
- a deterministic simulation stack focused on reproducibility and long-lived data.

It is not:
- a general-purpose rendering engine or game framework.
- a floating-point or wall-clock-driven authoritative simulation.
- a monolithic launcher/installer/game binary.

## High-level architecture (technical but accessible)
Domino (engine) provides the deterministic core. Dominium (game) implements the
authoritative rules and domain logic on top of it. The launcher and setup are
separate control-plane tools: setup installs and prepares the product, and the
launcher orchestrates runtime instances and hands the game an explicit launch
handshake. Client and server are entrypoints that link the engine and game.

Separation keeps authoritative simulation isolated from platform/UI and from
installation or repair logic while preserving deterministic boundaries.

## Key characteristics
- Determinism: fixed-point simulation and canonical ordering.
- Portability: C90/C++98 codebases with multiple platform backends.
- Long-term maintenance focus: stable layout and compatibility contracts.
- Explicit invariants: public headers and specs define behavior and ABI rules.
- Tooling-enforced discipline: static architecture checks and build guards.

## Intended audiences & use cases
- Players: packaged builds of the game and launcher.
- Modders: content packs and rule-driven extensions.
- Developers: engine/game/launcher/setup contributors.
- Researchers: reproducible simulation and verification workflows.

## Supported platforms (high level only)
- Presets target Windows (MSVC), Linux (GCC), and macOS (Xcode).
- Platform backends are selected via `DOM_PLATFORM` and are host-dependent;
  see `docs/BUILD_MATRIX.md` for the current preset list.

## Project structure (top-level map)
- `docs/` — authoritative specifications and policy docs
- `engine/` — Domino engine sources and public headers
- `game/` — Dominium game sources and public headers
- `client/` — client runtime entrypoint
- `server/` — server runtime entrypoint
- `launcher/` — launcher core and frontends
- `setup/` — setup core and frontends
- `tools/` — tool host and validators
- `libs/` — interface libraries and contracts
- `schema/` — data schema sources and validation references
- `sdk/` — SDK headers, docs, and samples
- `scripts/` — build and packaging helpers
- `cmake/` — CMake modules used by the root build
- `legacy/` — archived sources excluded from the root build graph
- `build/` — out-of-source build directory (ephemeral)
- `dist/` — dist layout outputs (ephemeral, opt-in)
- `.github/` — workflow and CI configuration

## Documentation map
- `docs/README.md` — documentation index and entry points
- `docs/ARCHITECTURE.md` — system architecture and layering
- `docs/COMPONENTS.md` — component roles and build products
- `docs/DEPENDENCIES.md` — allowed and forbidden dependency edges
- `docs/CONTRACTS.md` — public API contract rules
- `docs/BUILD_OVERVIEW.md` — build topology summary
- `docs/BUILDING.md` — build system and configuration
- `docs/BUILD_MATRIX.md` — canonical presets
- `docs/BUILD_DIST.md` and `docs/build_output.md` — dist layout and outputs
- `docs/SPEC_*.md` — subsystem specifications (see `docs/README.md`)

## Build & usage overview (non-procedural)
Builds produce the engine and game libraries, client/server entrypoints,
launcher/setup frontends, and tool executables. Default outputs go to the build
directory (`bin/` and `lib/`); the `dist/` layout is opt-in. Detailed build
instructions and presets live in `docs/BUILDING.md` and `docs/BUILD_MATRIX.md`.

## Project status & maturity
Status: active development. The core build graph is in place, and several
components still contain stub implementations (see `*_stub.c`) while the specs
define the long-term contracts.

## License
This repository is under the "Dominium Engine and Game - Restricted Source
Viewing License, Version 1.0 (Draft)". See `LICENSE.md`.
