# ARCH_REPO_LAYOUT — Canonical Repository Layout and Ownership

Status: draft
Version: 1

## Purpose
This document realigns the Domino engine and Dominium game plan to the canonical
repository layout. It defines ownership boundaries, directory mappings, and
enforcement rules without changing system design or simulation semantics.

## Canonical layout (authoritative)
Top-level products:
- `engine/`  Domino engine (reusable, pure)
- `game/`    Dominium game logic (reusable)
- `client/`  Player executable (presentation + input)
- `server/`  Authoritative simulation host
- `launcher/` Orchestration / runtime selection
- `setup/`   Installer / updater
- `tools/`   First-class tools
- `libs/`    Shared libraries (pure)
- `schema/`  Canonical data formats & schemas

## Dependency diagram (high-level)
```
           [schema]     [libs]
               |          |
               v          v
            [engine] ---->|
               |
               v
             [game]
            /     \
       [client]  [server]

[launcher] -> [libs] + [schema] + [engine public] (+ [game metadata if needed])
[setup]    -> [libs] + [schema]
[tools]    -> [libs] + [engine public] + [schema]
```

## Ownership rules (enforced)
- Only headers under `engine/include/` are public engine ABI.
- All `engine/modules/**` headers are private to engine targets.
- `game/` must include `domino/*` public headers only (no `engine/modules/**`).
- `launcher/`, `setup/`, and `tools/` must never include engine internals.
- Rendering backends live under `engine/render/`, not `client/`.
- Game logic, economy, doctrine, and UI semantics never live under `engine/`.

## Canonical engine ownership
```
engine/
  include/           public engine ABI only
  modules/
    core/            time, math, hashing, ordering
    ecs/             entity component system (engine primitives)
    sim/             events, ledgers, effect field primitives
    world/           coordinates, frames, WSS interfaces
    io/              TLV/container primitives
    sys/             minimal OS abstractions
  render/            render backends (sw/gl/vulkan/d3d/metal/null)
  tests/
  CMakeLists.txt
```
Notes:
- Current engine modules may be grouped into these canonical buckets. The
  mapping below is authoritative for planning and documentation regardless of
  internal subfolder names.

## Canonical game ownership
```
game/
  core/              orchestration & glue logic
  rules/             gameplay rules (effect fields, commands, doctrine)
  ai/                rule-based AI (deterministic)
  economy/           instruments, markets, taxation
  content/
    worldgen/
    factions/
    tech/
    scenarios/
  mods/              mod-facing validation & integration
  ui/                UI semantics & capability rules (no rendering)
  tests/
  CMakeLists.txt
```

## Major system ownership map (engine vs game vs tools vs schema)
Each system is split into engine primitives (deterministic mechanics) and game
rules/policy (meaning). Tools own authoring/inspection; schema owns formats.

Time (ACT, frames, scheduling)
- Engine: `engine/modules/core/`, `engine/modules/sim/`, `engine/modules/world/`
- Game: `game/core/`, `game/rules/`
- Tools: `tools/` (inspection)
- Schema: `schema/` (time serialization)

Calendars & standards
- Engine: `engine/modules/core/`
- Game: `game/rules/`
- Tools: `tools/` (authoring)
- Schema: `schema/` (calendar/standard formats)

World Source Stack (procedural + real data)
- Engine: `engine/modules/world/` (WSS interfaces)
- Game: `game/content/worldgen/`
- Tools: `tools/` (pipeline validation)
- Schema: `schema/` (source manifests)

Effect fields
- Engine: `engine/modules/sim/` (field primitives)
- Game: `game/rules/` (field meaning)
- Tools: `tools/` (debug/authoring)
- Schema: `schema/`

Information & fog-of-war
- Engine: `engine/modules/sim/` (information model primitives)
- Game: `game/rules/` (visibility policy)
- Tools: `tools/` (inspection)
- Schema: `schema/`

Communication & commands
- Engine: `engine/modules/sim/`, `engine/modules/io/`
- Game: `game/rules/` (command semantics)
- Tools: `tools/` (inspection)
- Schema: `schema/`

Doctrine & autonomy
- Engine: none (no game rules in engine)
- Game: `game/rules/`, `game/ai/`
- Tools: `tools/` (tuning)
- Schema: `schema/`

Fidelity projection & aggregation
- Engine: `engine/modules/sim/` (projection primitives)
- Game: `game/rules/` (policy)
- Tools: `tools/` (profiling)
- Schema: `schema/`

Provenance & construction
- Engine: `engine/modules/core/`, `engine/modules/world/` (provenance primitives)
- Game: `game/rules/` (construction law)
- Tools: `tools/` (audit)
- Schema: `schema/`

Economy, currency, markets, taxation
- Engine: none (no domain economy in engine)
- Game: `game/economy/`, `game/rules/`
- Tools: `tools/` (analytics)
- Schema: `schema/`

UI / HUD / Epistemic interface
- Engine: `engine/render/` (render backends only)
- Game: `game/ui/` (semantics, capability rules)
- Tools: `tools/ui_shared/`, `tools/` (authoring)
- Schema: `schema/` (UI schema)

Death, continuity, lineage
- Engine: none
- Game: `game/rules/`
- Tools: `tools/` (inspection)
- Schema: `schema/`

## Build strategy (CMake)
- `engine` builds as a reusable static library target `engine::domino`.
- `game` builds as a reusable static library target `game::dominium`.
- `client` and `server` link only `engine::domino` + `game::dominium`.
- `launcher` links `engine::domino` public API + `libs::contracts` + `schema/`.
- `setup` links `libs::contracts` + `schema/` only.
- `tools` link `libs::contracts` + `engine::domino` public API + `schema/`.

## Enforceable CMake boundaries
- Use `target_include_directories` with strict PUBLIC/PRIVATE separation.
- Public engine includes: `engine/include/` only.
- Game includes: `game/include/` only; engine internals are never in include
  paths for game targets.
- No global include directories (except generated config headers).
- Symbol visibility: public APIs are explicit; internal headers remain private.

## CI enforcement notes
These checks are mandatory for CI and local verification:
- Include boundary checks: `scripts/verify_includes_sanity.py`
  - Fails if game includes engine internals or engine references game.
- Tree sanity checks: `scripts/verify_tree_sanity.bat`
  - Fails if engine contains launcher/setup/tools directories or headers.
- Determinism gates: batch vs step determinism tests must match.
- Global iteration lint: disallow global iteration in deterministic contexts.
- Client UI rule: no modal loading flows (see `docs/SPEC_NO_MODAL_LOADING.md`).

## Contract ownership
Cross-product contracts live in `libs/contracts/include/dom_contracts/`.
Engine must not include `dom_contracts/*`. Game, launcher, setup, and tools may.
