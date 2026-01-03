# Dominium Game

This folder hosts the standalone game runtime, frontends, and launcher-mode
integration glue.

## Launcher filesystem contract
The game never consumes absolute paths from the handshake. All filesystem access
resolves through launcher-provided roots (see `docs/SPEC_FS_CONTRACT.md`).

Required environment in launcher mode:
- `DOMINIUM_RUN_ROOT` (required): per-run writable root for outputs.
- `DOMINIUM_HOME` (required for instance reads): logical instance/content root
  (`instances/`, `repo/`).
- When both are set, `DOMINIUM_RUN_ROOT` is authoritative for outputs.

## Run root layout (outputs)
`DOMINIUM_RUN_ROOT` is a per-run sandbox. Outputs are scoped beneath it:
- `saves/`
- `replays/`
- `logs/`
- `cache/`
- `refusal.tlv` (when refusing to start)

## Save/replay paths
- `--save` and `--load` resolve under `DOMINIUM_RUN_ROOT/saves/` in launcher mode.
- `--record-replay` and `--play-replay` resolve under `DOMINIUM_RUN_ROOT/replays/`
  in launcher mode.
- Absolute paths are rejected in launcher mode.

## Dev / standalone mode
For local runs without launcher roots, pass `--dev-allow-ad-hoc-paths=1` to allow:
- DOMINIUM_HOME discovery or cwd fallback.
- absolute save/replay/load paths.

This override is logged and must not be used for launcher runs.

## Docs
- `docs/SPEC_FS_CONTRACT.md`
- `docs/SPEC_GAME_CLI.md`
