# Dominium / Domino
Dominium is a deterministic world runtime and law-governed simulation OS. The
engine/game split is non-negotiable, and authoritative outcomes are reproducible
across builds. Existence, travel, authority, and time perception are explicit,
data-defined, and auditable.

## What this project is (non-technical)
Dominium provides a deterministic simulation runtime and the surrounding product
stack needed to install, launch, and run it. It is designed so the same inputs
produce the same results across supported builds, enabling reproducible saves,
replays, and verification.

It is:
- a deterministic world runtime with law-governed authority.
- a multi-scale reality model with explicit existence and refinement.
- a product stack (engine + game + client/server + launcher/setup + tools).
- a host for player-only, AI-only, mixed, spectator, anarchy, and admin worlds.

It is not:
- a traditional game engine or tick-everything sandbox.
- a modes-based game (laws and capabilities define behavior).
- a cheat-based admin system or a monolithic binary.
- a floating-point or wall-clock-driven authoritative simulation.

## Read this first (required)
This is not a typical game project. Contributors must read `docs/arch/` first.
- `docs/arch/WHAT_THIS_IS.md`
- `docs/arch/WHAT_THIS_IS_NOT.md`
- `docs/arch/CANONICAL_SYSTEM_MAP.md`
- `docs/arch/INVARIANTS.md`
- `docs/arch/ARCH0_CONSTITUTION.md`
- `docs/arch/CHANGE_PROTOCOL.md`

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
- Law-gated authority: capabilities + policy + law gates at intent/task/commit.
- Law-gated Work IR: authoritative work is emitted as TaskGraph/AccessSet and
  evaluated by existence/capability/policy gates before execution and commit.
- Multi-scale refinement: macro state is valid; micro detail is on-demand.
- Portability: baseline C90/C++98 builds with optional modern presets.
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
  see `docs/ci/BUILD_MATRIX.md` for the current preset list.

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
- `data/` — runtime-configurable content and profiles
- `schema/` — data schema sources and validation references
- `sdk/` — SDK headers, docs, and samples
- `scripts/` — build and packaging helpers
- `cmake/` — CMake modules used by the root build
- `legacy/` — archived sources excluded from the root build graph
- `build/` — out-of-source build directory (ephemeral)
- `dist/` — dist layout outputs (ephemeral, opt-in)
- `.github/` — workflow and CI configuration

## Documentation map
- `docs/guides/README.md` — documentation index and entry points
- `docs/arch/WHAT_THIS_IS.md` and `docs/arch/WHAT_THIS_IS_NOT.md` — scope and non-goals
- `docs/arch/CANONICAL_SYSTEM_MAP.md` — canonical dependency map
- `docs/arch/INVARIANTS.md` — hard invariants
- `docs/arch/ARCH0_CONSTITUTION.md` — architectural constitution (binding)
- `docs/arch/CHANGE_PROTOCOL.md` — required process for sim-affecting change
- `docs/arch/FUTURE_PROOFING.md` — long-term guardrails and evolution rules
- `docs/arch/EXTENSION_RULES.md` — how new systems are added safely
- `docs/arch/SCALE_AND_COMPLEXITY.md` — macro/micro scale model and limits
- `docs/arch/UNKNOWN_UNKNOWNS.md` — handling new paradigms without refactor
- `docs/arch/ARCH_CHANGE_PROCESS.md` — architectural change checklist
- `docs/arch/REALITY_MODEL.md` — unified existence/refinement/domain/travel model
- `docs/arch/AUTHORITY_MODEL.md` — authority and capability summary
- `docs/arch/EXECUTION_MODEL.md` — Work IR and performance summary
- `docs/arch/DIRECTORY_CONTEXT.md` and `docs/arch/ARCH_REPO_LAYOUT.md` — layout boundaries
- `docs/arch/ARCHITECTURE.md` — system architecture and layering
- `docs/arch/GLOSSARY.md` — canonical terminology
- `docs/arch/LAW_ENFORCEMENT_POINTS.md` — law gates and enforcement phases
- `docs/arch/ADOPTION_PROTOCOL.md` — incremental migration rules for Work IR adoption
- `schema/execution/README.md` and `schema/law/README.md` — execution and law schemas
- `schema/ecs/README.md` — ECS component schema and storage backend policy
- `docs/arch/EXECUTION_REORDERING_POLICY.md` and `docs/arch/DETERMINISTIC_REDUCTION_RULES.md` — deterministic reordering and reduction rules
- `docs/guides/DEPENDENCIES.md` — allowed and forbidden dependency edges
- `docs/guides/WORK_IR_EMISSION_GUIDE.md` — how game systems emit Work IR and Access IR
- `docs/guides/KERNEL_BACKEND_SELECTION.md` — kernel backend selection policy
- `docs/specs/CONTRACTS.md` — public API contract rules
- `docs/guides/BUILD_OVERVIEW.md` — build topology summary
- `docs/guides/BUILDING.md` — build system and configuration
- `docs/ci/BUILD_MATRIX.md` — canonical presets
- `docs/guides/BUILD_DIST.md` and `docs/guides/build_output.md` — dist layout and outputs
- `docs/ci/CI_ENFORCEMENT_MATRIX.md` — CI checks enforcing ARCH0/EXEC*
- `docs/ci/FUTURE_ENFORCEMENT.md` — FUTURE0 enforcement notes
- `docs/app/README.md` — application runtime and CLI docs
- `docs/platform/README.md` — platform runtime and lifecycle docs
- `docs/render/README.md` — renderer interface and backend docs
- `docs/specs/SPEC_*.md` — subsystem specifications (see `docs/specs/SPEC_INDEX.md`)
- `MODDING.md` — modding policy and boundaries
- `GOVERNANCE.md` — project governance summary
- `schema/schema_policy.md` and `schema/mod_extension_policy.md` — schema/mod extension rules

## Build & usage overview (non-procedural)
Builds produce the engine and game libraries, client/server entrypoints,
launcher/setup frontends, and tool executables. Default outputs go to the build
directory (`bin/` and `lib/`); the `dist/` layout is opt-in. Detailed build
instructions and presets live in `docs/guides/BUILDING.md` and `docs/ci/BUILD_MATRIX.md`.

## Project status & maturity
Status: active development. The core build graph is in place, and several
components still contain stub implementations (see `*_stub.c`) while the specs
define the long-term contracts.

## License
This repository is under the "Dominium Engine and Game - Restricted Source
Viewing License, Version 1.0 (Draft)". See `LICENSE.md`.
