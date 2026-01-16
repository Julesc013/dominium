--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

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
# Game CLI

Status: v1
Version: 1

This document defines the canonical CLI contract for the Dominium game runtime.

## Contract

Usage:
`game_dominium [options]`

### Modes
- `--mode=gui|tui|headless`

### Network / roles
- `--server=off|listen|dedicated`
- `--connect=<addr[:port]>`
- `--port=<u16>`

### Headless / automation
- `--auto-host` (auto-start host session)
- `--headless-ticks=<u32>` (exit after N in-session ticks)
- `--headless-local=0|1` (run local single-player session without sockets)

### Instance / content
- `--home=<path>` (DOMINIUM_HOME override; dev/standalone only)
- `--instance=<id>`
- `--profile=compat|baseline|perf`
- `--handshake=<path>` (launcher handshake TLV; relative to DOMINIUM_RUN_ROOT in launcher mode)

### Backends
- `--gfx=<backend>` (canonical gfx backend selector)
- `--sys.<subsystem>=<backend>` (canonical subsystem override)
- `--platform=<backend>` (deprecated alias for platform/dsys backend)

### Tick / determinism
- `--tickrate=<ups>`
- `--lockstep-strict=0|1`
- `--deterministic-test`

### Replay
- `--record-replay=<path>` (relative to DOMINIUM_RUN_ROOT/replays in launcher mode)
- `--play-replay=<path>` (relative to DOMINIUM_RUN_ROOT/replays in launcher mode)
- `--replay-strict-content=0|1`

### Save / load
- `--save=<path>` (relative to DOMINIUM_RUN_ROOT/saves in launcher mode)
- `--load=<path>` (relative to DOMINIUM_RUN_ROOT/saves in launcher mode)

### Filesystem / launcher mode
- The game resolves filesystem access via `DOMINIUM_RUN_ROOT` and/or
  `DOMINIUM_HOME` per `docs/SPEC_FS_CONTRACT.md`.
- `--handshake` enables launcher mode; absolute save/replay/load paths are
  rejected unless the dev override is enabled.
- `--dev-allow-ad-hoc-paths=0|1` explicitly allows local standalone runs without
  launcher roots and permits absolute paths (logged, not for launcher use).
- `--dev-allow-missing-content=0|1` allows empty content packs/mods in dev/test
  runs (logged, not for launcher use).

### Compatibility / introspection
- `--capabilities`
- `--print-caps`
- `--print-selection`
- `--introspect-json`
- `--help` / `-h`

### Reserved launcher flags
Launcher integration flags are accepted but not required:
`--launcher-*` (ignored by the game runtime unless explicitly wired).

## Alias and deprecation rules
- `--renderer=<backend>` is an alias for `--gfx=<backend>`. The first use emits a one-time warning to stderr.
- `--platform=<backend>` is a deprecated alias for the platform backend. Prefer `--sys.dsys=<backend>` (or project-specific subsystem keys).
- `--server` (no value) is treated as `--server=dedicated`.
- `--listen` is treated as `--server=listen`.

## Exit codes
- `0`: success (including `--help`, `--capabilities`, `--introspect-json`).
- `1`: runtime init or execution failure.
- `2`: invalid CLI arguments or parse errors.

## Output behavior
- `--help`: prints usage to stdout and exits `0`. Any parse error prints a brief message to stderr and exits `2`.
- `--capabilities`: prints a JSON document to stdout and exits `0`. No stderr output unless an internal error occurs.
- `--introspect-json`: prints product info JSON to stdout and exits `0`. No stderr output unless an internal error occurs.
- `--print-caps` / `--print-selection`: print human-readable capability/selection logs to stdout (selection errors to stderr) and exit `0` on success or `2` if selection fails.

