Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. This spec is implemented under `launcher/`.

GAME:
- None. This spec is implemented under `launcher/`.

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# Launcher Net Sessions

## Game CLI Flags

Dominium Game supports session control flags (see `source/dominium/game/dom_game_cli.cpp`):

- `--listen` : start a local host (host + local player)
- `--server` : start a dedicated host
- `--connect=<addr>` : connect as a client (host address; port provided via `--port=` or embedded in the address if supported)
- `--port=<NNN>` : listen/connect port (default `7777`)

These flags map to the engine session roles (`SINGLE/HOST/CLIENT`) and drive the Dominium-side transport setup.

## Launcher UI Flow

`dominium-launcher` (see `source/dominium/launcher/`) provides simple session controls:

- **Start Local Host**: spawns the game with `--listen --port=<port> --instance=<id>`.
- **Start Dedicated Host**: spawns the game with `--server --mode=headless --port=<port> --instance=<id>`.
- **Connect To Host**: spawns the game with `--connect=<host> --port=<port> --instance=<id>`.

Instance selection is required so both host and clients load compatible content and version info for handshake/compat checks.

## Cross-Instance Orchestration

The launcher can spawn multiple game processes:

- Start a host (listen or dedicated).
- Press **Connect To Host** multiple times to spawn multiple clients connecting to the same host/port.