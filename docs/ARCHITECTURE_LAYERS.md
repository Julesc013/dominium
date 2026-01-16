# Architecture Layers

This repo enforces product boundaries via CMake target scopes and sanity checks
to keep the engine pure and prevent cross-layer leakage.

## Product Boundaries (Summary)
- Engine: pure reusable core. Public headers under `engine/include/domino`.
- Game: depends on engine public API only. Public headers under `game/include/dominium`.
- Launcher: depends on libs + engine public API + schema. No engine internals.
- Setup: depends on libs + schema only. No engine/launcher internals.
- Tools: use tools shared runtime + libs + engine public API + schema. No setup/launcher internals.

## Target Graph (Current)
- `engine::domino` (`engine_domino`)
- `libs::base`, `libs::crypto`, `libs::fsmodel`, `libs::netproto`
- `setup::setup`, `setup::cli`, `setup::gui`, `setup::tui`
- `launcher::launcher`, `launcher::cli`, `launcher::gui`, `launcher::tui`
- `tools::shared`, `tools::host`, `tools::coredata_compile`, `tools::coredata_validate`
- `game::dominium`, `dominium_client`, `dominium_server`

## Include Ownership
- `engine/include/domino/**` => engine public API
- `game/include/dominium/**` => game public API
- `setup/include/dsk/**` + `setup/include/dsu/**` => setup public API
- `tools/ui_shared/include/**` => tool/UI shared public API

## Mechanical Gates
- `scripts/verify_tree_sanity.bat`
- `scripts/verify_includes_sanity.py`
- `engine_include_sanity` custom target (CMake)
