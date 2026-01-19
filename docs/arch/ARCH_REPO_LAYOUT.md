# ARCH_REPO_LAYOUT — Canonical Repository Layout and Ownership

Status: draft
Version: 2

## Purpose
This document defines the current directory layout and ownership boundaries for
the Domino engine and Dominium products. It describes what exists today and the
enforcement rules that keep boundaries intact.

## Canonical layout (authoritative)
Top-level domains:
- `engine/` — Domino engine library sources and headers.
- `game/` — Dominium game library sources and headers.
- `client/` — client executable entrypoint.
- `server/` — server executable entrypoint.
- `launcher/` — launcher core library and frontends.
- `setup/` — setup core library and frontends.
- `tools/` — tool host, validators, and editors.
- `libs/` — interface libraries and shared contracts.
- `data/` — runtime-configurable content and profiles.
- `schema/` — data schemas and validation docs (data-only).
- `sdk/` — public SDK headers, docs, and samples.
- `docs/` — architecture, policies, specs, CI rules, and guides.
- `legacy/` — archived sources excluded from current builds and checks.

## Dependency summary (high level)
- `engine/` has no top-level dependencies.
- `game/` depends on `engine/` (public headers + library).
- `client/` and `server/` depend on `engine/` + `game/`.
- `launcher/` depends on `engine/` (public headers) + `libs/contracts`.
- `setup/` depends on `libs/contracts`.
- `tools/` depend on `libs/contracts`; select tools also depend on `engine/`.
- `schema/` and `sdk/` are data/doc domains with no build targets.

## Ownership rules (enforced)
- Public engine headers: `engine/include/**` only.
- Engine internals: `engine/modules/**` and `engine/render/**` are private.
- Game code must not include `engine/modules/**`.
- Launcher/setup/tools must not include engine internals.
- Render backends live under `engine/render/**`, not under `client/` or `game/`.
- Game rules and economy never live under `engine/`.

## Engine ownership (current directories)
```
engine/
  include/           public engine ABI only
  modules/           engine subsystems (core, sim, execution, world, net, etc.)
  render/            render backends and renderer-facing glue (legacy path)
  tests/             engine tests (optional build)
  CMakeLists.txt
```

## Game ownership (current directories)
```
game/
  core/              game-level orchestration and shared logic
  rules/             authoritative rules and domain logic
  mods/              mod-facing integration
  ui/                UI semantics (non-rendering)
  tests/             game tests and fixtures
  CMakeLists.txt
```

## Build strategy (CMake)
- `engine` builds as static library `engine::domino`.
- `game` builds as static library `game::dominium`.
- `client` and `server` link `engine::domino` + `game::dominium`.
- `launcher` builds `launcher::launcher` and frontends (`launcher_cli`, `launcher_gui`, `launcher_tui`).
- `setup` builds `setup::setup` and frontends (`setup_cli`, `setup_gui`, `setup_tui`).
- `tools` builds `tools::shared`, `tools::host`, `tools::data_validate`, and `tools::validate_all` plus stubs.

## Enforceable boundaries
- CMake uses target-scoped include/link rules; no `include_directories()` or `link_directories()`.
- Root `CMakeLists.txt` asserts forbidden links with `dom_assert_no_link(...)`.
- `tools/ci/arch_checks.py` enforces include and dependency boundaries.

## Contract ownership
Cross-product contracts live in `libs/contracts/include/dom_contracts/`.
`engine` does not link `libs::contracts`; launcher/setup/tools do.
