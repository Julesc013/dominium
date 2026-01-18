# Architecture Layers

This repo enforces product boundaries via CMake target scopes and CI checks to
keep the engine isolated and prevent cross-layer leakage.

## Product boundaries (summary)
- Engine: reusable core (`engine/`). Public headers under `engine/include/domino/`.
- Game: depends on engine public API only (`game/`). Public headers under `game/include/dominium/`.
- Launcher: links `engine::domino` + `libs::contracts` only; no engine internals.
- Setup: links `libs::contracts` only; no engine/game/launcher internals.
- Tools: link `tools::shared` + `libs::contracts`; select tools also link `engine::domino`.
- Client/Server: link `engine::domino` + `game::dominium`.

## Target graph (current)
- `engine::domino` (`domino_engine`)
- `game::dominium` (`dominium_game`)
- `dominium_client`, `dominium_server`
- `launcher::launcher`, `launcher::cli`, `launcher::gui`, `launcher::tui`
- `setup::setup`, `setup::cli`, `setup::gui`, `setup::tui`
- `tools::shared`, `tools::host`, `tools::coredata_compile`, `tools::coredata_validate`
- `tools::data_validate`, `tools::validate_all`
- `libs::base`, `libs::crypto`, `libs::fsmodel`, `libs::netproto`, `libs::contracts`

## Include ownership
- `engine/include/domino/**` ⇒ engine public API.
- `game/include/dominium/**` ⇒ game public API.
- `launcher/include/launcher/**` ⇒ launcher public API.
- `setup/include/dsk/**` and `setup/include/dsu/**` ⇒ setup public API.
- `tools/ui_shared/include/**` ⇒ tool/UI shared public API (where used).

## Mechanical gates
- `scripts/verify_includes_sanity.py`
- `scripts/verify_cmake_no_global_includes.py`
- `tools/ci/arch_checks.py` (via `check_arch` target)
