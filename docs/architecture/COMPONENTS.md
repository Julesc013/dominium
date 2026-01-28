# Components

This document describes the current top-level components and their build
products. It complements `docs/architecture/ARCHITECTURE.md` and
`docs/guides/DEPENDENCIES.md`. Directory layout is authoritative in
`docs/architecture/DIRECTORY_CONTEXT.md`.

## Engine (`engine/`)
- Role: Domino deterministic engine library (authoritative simulation + runtime subsystems).
- Build products: `domino_engine` (static library; aliases include `engine::domino`).
- Public API: `engine/include/domino/**`.
- Consumers: `game/`, `client/`, `server/`, `launcher/`, and select tools.

## Game (`game/`)
- Role: Dominium game rules and domain logic (authoritative).
- Build products: `dominium_game` (static library).
- Public API: `game/include/dominium/**`.
- Consumers: `client/` and `server/`.

## Client (`client/`)
- Role: Client runtime entrypoint.
- Build products: `dominium_client` (output name `client`).
- Links: `domino_engine` + `dominium_game`.

## Server (`server/`)
- Role: Server runtime entrypoint.
- Build products: `dominium_server` (output name `server`).
- Links: `domino_engine` + `dominium_game`.

## Launcher (`launcher/`)
- Role: Control plane and instance orchestration.
- Build products: `launcher_core` (static), `launcher_cli`, `launcher_gui`, `launcher_tui`.
- Public API: `launcher/include/launcher/**`.
- Links: `engine::domino`, `libs::contracts`.

## Setup (`setup/`)
- Role: Installer/setup workflows.
- Build products: `setup_core` (static), `setup_cli`, `setup_gui`, `setup_tui`.
- Public API: `setup/include/dsk/**` and `setup/include/dsu/**`.
- Links: `libs::contracts`.

## Tools (`tools/`)
- Role: Offline tools and validators.
- Build products: `tools_shared` (static), `dominium-tools`, `coredata_compile`,
  `coredata_validate`, `data_validate`, `validate_all`.
- Links:
  - `tools_shared` and `dominium-tools` link `libs::contracts`.
  - `data_validate` links `domino_engine`.
- Tests: `validate_all` registers fixture tests against
  `tools/validation/fixtures/**` when tools are built.

## Libraries (`libs/`)
- Role: Interface libraries and shared contracts.
- Public API: `libs/contracts/include/dom_contracts/**`.

## Schemas (`schema/`)
- Role: Data schema sources and validation references (data-only; no build targets).

## Legacy (`legacy/`)
- Role: Archived sources excluded from the root build graph.

## See also
- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/ARCHITECTURE_LAYERS.md`
- `docs/architecture/CANONICAL_SYSTEM_MAP.md`
- `docs/architecture/DIRECTORY_CONTEXT.md`
