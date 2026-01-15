# Dominium Game

This folder hosts the standalone game runtime, frontends, and launcher-mode
integration glue.

## Play flow (high level)
The runtime owns the play-flow phase machine:
`BOOT -> SPLASH -> MAIN_MENU -> SESSION_START -> SESSION_LOADING -> IN_SESSION -> SHUTDOWN`.
See `docs/SPEC_PLAY_FLOW.md` for full transition rules and refusal behavior.

## Launcher integration
The launcher is the control plane. It provides environment roots and a handshake:
- `DOMINIUM_RUN_ROOT` (required in launcher mode): per-run writable root.
- `DOMINIUM_HOME` (required for instance reads): logical instance/content root.
- `--handshake=handshake.tlv` is passed relative to `DOMINIUM_RUN_ROOT`.
No absolute paths are accepted in the handshake. See `docs/SPEC_FS_CONTRACT.md`.

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
For local runs without launcher roots:
- Pass `--dev-allow-ad-hoc-paths=1` to allow DOMINIUM_HOME discovery or cwd fallback.
- Pass `--dev-allow-missing-content=1` to run without packs/mods (dev/test only; logged).
- Optionally override `--home=<path>` and `--instance=<id>`.

## Headless automation
Headless mode runs the same phase machine without a window:
- `--mode=headless` uses the null system backend by default.
- `--auto-host` auto-starts a host session (join uses `--connect`).
- `--headless-local=1` runs a local single-player session without binding sockets.
- `--headless-ticks=<u32>` exits after N in-session ticks.

## Headless smoke test
Example (run from the repo or build directory):
```sh
game_dominium --mode=headless --auto-host --headless-local=1 --headless-ticks=10 --dev-allow-ad-hoc-paths=1 --dev-allow-missing-content=1 --instance=headless_smoke
```

## Docs
- `docs/SPEC_PLAY_FLOW.md`
- `docs/SPEC_FS_CONTRACT.md`
- `docs/SPEC_GAME_CLI.md`
