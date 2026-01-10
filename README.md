# Dominium / Domino
Dominium (built on the Domino engine) is a deterministic 3D simulation-type game runtime.

## High-level overview (non-technical)
Dominium combines a deterministic simulation engine (Domino) with product code
for a game, launcher, setup tools, and editors. Its focus is reproducibility:
given the same inputs, the simulation produces the same outcomes, replays, and
hashes across supported platforms.

What makes it distinct:
- Uses fixed-point math and strict ordering rules to keep results stable.
- Separates authoritative simulation from user interface, rendering, and
  platform code.
- Treats its repository layout and specs as long-term compatibility contracts.

Problems it is designed to solve:
- Replayable, verifiable simulations that stay consistent across machines.
- Lockstep-style workflows where every peer must agree on results.
- Long-lived content and save formats with explicit versioning rules.

Non-goals (by design constraints):
- Not a floating-point or wall-clock-driven simulation core.
- Not a general-purpose engine that mixes user interface or rendering with
  authoritative state.
- Not a build that downloads dependencies at configure or build time.

## Key features (at a glance)
- Deterministic C90 simulation core with fixed-point math and world hashing.
- C++98 product layer (game, launcher, setup, tools) on top of stable contracts.
- Replay and lockstep scaffolding with canonical ordering rules.
- Strict dependency boundaries and public-header API contracts.
- Multiple platform and renderer backends selected at configure time.
- Built-in determinism regression scans and test suites.
- No build-time network downloads; vendored sources live under `external/`.

## Architecture overview (mid-level technical)
Layering (simplified):
- Dominium products: game, launcher, setup, tools
  - Dominium common layer: paths, instances, packsets, compatibility
- Domino engine
  - Deterministic core: sim, world, TRANS/STRUCT/DECOR (transport, structure,
    decor), replay, hashing
  - Derived presentation: rendering and user interface (UI) view
    (non-authoritative)
- Domino system layer (dsys): operating system, window, input, filesystem,
  process backends

Major subsystems and roles:
- **Domino deterministic core**: authoritative simulation state, fixed-point
  math, canonical ordering, replay and world hashing.
- **Domino system layer**: platform abstractions; must not influence simulation
  outcomes.
- **Rendering and user interface (UI)**: derived outputs only; never a source
  of truth.
- **Dominium products**: game runtime, launcher, setup/packaging, and tools
  built on the public engine contracts in `include/`. Tools are launched as
  instance targets and consume the same handshake + logical roots; they do not
  bypass launcher contracts.
- **Runtime filesystem roots**: launcher-defined logical roots (read-only
  `DOMINIUM_HOME`, per-run writable `DOMINIUM_RUN_ROOT`); the game does not
  infer install layouts.

### Runtime kernel (game layer)
Domino is the deterministic simulation engine (C90/C89, fixed-point). Dominium
is the product layer (game, launcher, setup, tools) built around it. The
Dominium game contains a runtime kernel that orchestrates simulation ticks,
ingests commands, computes determinism hashes, binds saves/replays, and
validates the launcher handshake; GUI/TUI/headless frontends never touch engine
state directly, and rendering/UI remain derived views.

**Deterministic time model (tick-first):** authoritative time is `tick_index`
(u64) and `ups` (ticks per second, default 60). Wall-clock seconds/days are
derived for presentation; floating-point `dt` may exist in UI/runtime glue but
never drives simulation.

**Units and scale:** canonical length unit is meters; positions are stored as
fixed-point Q16.16 meters. One tile/block equals 1 meter and one chunk equals
16 meters by definition; larger groupings (segment, page, surface) are a
conceptual hierarchy. Rendering and cache grids are non-authoritative.

**Instance model and identity binding:** the instance is the top-level unit of
reproducibility (isolated, hashable, reproducible). World state, saves, replays,
and logs are instance-scoped; there is no mutable global universe directory.
Saves and replays bind to instance identity, content/pack graph + hashes, and
sim-affecting flags; mismatches refuse to run by default to support archival
verification (`docs/SPEC_IDENTITY.md`, `docs/SPEC_GAME_PRODUCT.md`).

**Launcher/setup control plane:** Setup2 (the current setup core) is the
kernel-centric installer and deployment engine; the launcher is the long-lived
control plane. The game does not install, repair, migrate, or guess paths, and
it must not scan or infer install layouts. It accepts instance identity
(`instance_id`), content hashes, and flags from the launcher handshake and
refuses to run on mismatch
(`docs/SPEC_LAUNCHER.md`, `docs/SPEC_SETUP_CORE.md`,
`docs/LAUNCHER_SETUP_OVERVIEW.md`). `launcher_handshake.tlv` must not contain
absolute paths; filesystem access is resolved through launcher-defined logical
roots (`DOMINIUM_HOME` read-only, `DOMINIUM_RUN_ROOT` per-run writable) with
relative, declarative paths only.

Design philosophy highlights:
- Determinism first: fixed-point, canonical order, replayable state.
- Portability: C90/C++98 targets and explicit platform backends.
- Explicit contracts: public headers define the ABI and behavior.
- Long-term maintainability: specs and layout contracts are authoritative.

Further reading: `docs/ARCHITECTURE.md`, `docs/OVERVIEW_ARCHITECTURE.md`,
`docs/SPEC_DOMINIUM_LAYER.md`, `docs/SPEC_DOMINO_SUBSYSTEMS.md`.

## Supported platforms (summary)
- Primary validated: Windows `win32` and `win32_headless` (see
  `docs/BUILD_MATRIX.md`).
- Secondary / compile-gated: `posix_headless`, `posix_x11`, `posix_wayland`,
  `cocoa` (host dependencies required; see `docs/BUILD_MATRIX.md`).
- Headless/CI (continuous integration): `null` platform with `null` renderer
  backend.
- Renderer backends: software baseline; optional `dx9`, `dx11`, `gl2`, `vk1`,
  `metal` when host tooling is available.
- Legacy installer stubs: DOS, Win16, CP/M-80, CP/M-86, Carbon OS
  (`docs/SETUP_RETRO.md`).
- Architectural constraints: little-endian, two's complement, arithmetic right
  shift, truncating signed division; packaging templates name `amd64`/`x86_64`
  by default (`docs/SETUP_LINUX.md`).

## Intended audience and use cases
For:
- Engine developers who need deterministic simulation, replay, and hashing.
- Teams building a game + launcher + setup workflow with strict layering.
- Researchers/educators who need reproducible simulations over time.

Not for:
- Projects that require floating-point authoritative physics or time-based
  simulation in the core.
- Teams expecting modern C++ features (run-time type information, exceptions,
  or STL types across the ABI boundary) or large dynamic dependency stacks.

## Design constraints and philosophy
- **Language standards**: deterministic core is C90; product layer is C++98
  (see `docs/LANGUAGE_POLICY.md`).
- **Determinism**: fixed-point math only, canonical ordering, replay/hash
  invariants, no wall-clock or OS APIs in authoritative paths
  (`docs/SPEC_DETERMINISM.md`).
- **Dependencies**: no build-time downloads; external code is vendored under
  `external/` (`docs/BUILDING.md`, `docs/DEPENDENCIES.md`).
- **Contracts**: public headers are the application binary interface (ABI) and
  must be self-contained; data structs are plain-old-data (POD) and versioned
  when crossing module boundaries (`docs/CONTRACTS.md`).
- **Layering**: engine core never depends on product code; platform/user
  interface/render layers must not influence authoritative state
  (`docs/DEPENDENCIES.md`).

These constraints exist to keep simulation results reproducible and maintainable
across platforms and over long time horizons.

## Repository structure (map)
- `docs/` - specifications and policy documents (authoritative)
- `include/` - public headers (`include/domino/**`, `include/dominium/**`)
- `source/` - implementation code (`domino`, `dominium`, `tests`)
- `tests/` - integration tests and fixtures
- `data/` - in-tree content sources
- `repo/` - runtime repo content referenced via `DOMINIUM_HOME` (read-only)
- `tools/` - build-time and authoring tools
- `scripts/` - build and packaging helpers
- `cmake/` - CMake modules
- `external/` - vendored third-party sources
- `.github/` - CI and workflow config

## Documentation map
Start here:
- `docs/README.md` (documentation index)
- `docs/DIRECTORY_CONTEXT.md` (authoritative layout contract)
- `docs/ARCHITECTURE.md` and `docs/OVERVIEW_ARCHITECTURE.md`
- `docs/DEPENDENCIES.md` (allowed dependency directions)
- `docs/CONTRACTS.md` (public API rules)
- `docs/STYLE.md` (style and naming)
- `docs/LANGUAGE_POLICY.md` (language/toolchain constraints)

Build and release:
- `docs/BUILDING.md`
- `docs/BUILD_MATRIX.md`
- `docs/RELEASE_NOTES_PROCESS.md`

Subsystem specs (selected; see `docs/README.md` for the full list):
- `docs/SPEC_DETERMINISM.md`
- `docs/DETERMINISM_REGRESSION_RULES.md`
- `docs/SPEC_DOMINO_SUBSYSTEMS.md`
- `docs/SPEC_DOMINIUM_LAYER.md`
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_ACTIONS.md`
- `docs/SPEC_GAME_PRODUCT.md`
- `docs/SPEC_LAUNCHER.md`
- `docs/SPEC_SETUP_CORE.md`
- `docs/SPEC_SETUP_CLI.md`
- `docs/SPEC_TOOLS_CORE.md`

## Documentation Standards
Documentation density ratios act as a drift detector for under- or over-
documentation. A CMake quality gate checks comment line/word/char ratios, warns
locally, and fails in CI. See `docs/DOCUMENTATION_STANDARDS.md` for definitions,
thresholds, and tuning.

## Build / usage (high-level only)
Builds are CMake-based (minimum 3.16) and do not fetch network dependencies.
Use the presets in `CMakePresets.json` or follow `docs/BUILDING.md`. Platform
setup and packaging workflows are documented in `docs/SETUP_WINDOWS.md`,
`docs/SETUP_LINUX.md`, `docs/SETUP_MACOS.md`, and `docs/SETUP_RETRO.md`.
Runtime launch is normally mediated by the launcher control plane; standalone
execution is supported only in explicit dev-mode flows (`docs/SPEC_GAME_PRODUCT.md`,
`docs/SPEC_LAUNCHER.md`).

Dist output: final link artifacts are routed into the deterministic `dist/`
tree described in `docs/BUILD_DIST.md` and `docs/build_output.md`.

## Project status and maturity
Status: active development with a v0 deterministic core bootstrap in progress
(`docs/MILESTONES.md`). The Windows baseline configurations in
`docs/BUILD_MATRIX.md` are the primary validated targets; other backends are
compile-gated and may be incomplete. Expect specs to lead implementation.

## License
This repository is under the "Dominium Engine and Game - Restricted Source
Viewing License, Version 1.0 (Draft)". See `LICENSE`.

## Contributing / contact
Contributions are spec-driven and must preserve determinism and layering. Start
with `CONTRIBUTING.md` and follow the policies in `docs/STYLE.md`,
`docs/LANGUAGE_POLICY.md`, and `docs/DEPENDENCIES.md`. The security policy and
reporting expectations are in `SECURITY.md`.
