Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: `contracts/repo/layout.contract.toml` for current source repo layout convergence authority
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: `contracts/repo/layout.contract.toml` plus `docs/repo/REPO_LAYOUT_TARGET.md`

# ARCH_REPO_LAYOUT — Canonical Repository Layout and Ownership

## CONVERGE-02 Notice

This document is retained as legacy/reference material. It is not the current machine-readable source repo layout authority.

Current convergence authority:

- source layout contract: `contracts/repo/layout.contract.toml`
- root allowlist contract: `contracts/repo/root_allowlist.toml`
- human target explanation: `docs/repo/REPO_LAYOUT_TARGET.md`

Do not use this document alone to decide new paths.

## CONVERGE-12 Final Layout Note

Any later `canonical`, `authoritative`, or `current directory layout` wording in this file is retained as historical architecture context only. For current physical source repository layout authority, use `contracts/repo/layout.contract.toml`, `contracts/repo/root_allowlist.toml`, `contracts/repo/layout_exceptions.toml`, and `docs/repo/REPO_LAYOUT_TARGET.md`.

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: ownership intent remains useful, but the concrete top-level layout is stale relative to the real repository tree
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.






Status: draft


Version: 2





## Purpose


This document defines the current directory layout and ownership boundaries for


the Domino engine and Dominium products. It describes what exists today and the


enforcement rules that keep boundaries intact.





## Legacy Canonical Layout (Superseded For Physical Paths)


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


- Engine internals: `engine/modules/**` and `runtime/render/**` are private.


- Game code must not include `engine/modules/**`.


- Launcher/setup/tools must not include engine internals.


- Render backends live under `runtime/render/**`, not under `client/` or `game/`.


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





## See also


- `docs/architecture/DIRECTORY_CONTEXT.md`


- `docs/architecture/ARCHITECTURE_LAYERS.md`


- `docs/architecture/CANONICAL_SYSTEM_MAP.md`
