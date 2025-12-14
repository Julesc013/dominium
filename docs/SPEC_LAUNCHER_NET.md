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

