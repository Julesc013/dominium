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

### Instance / content
- `--home=<path>` (DOMINIUM_HOME override)
- `--instance=<id>`
- `--profile=compat|baseline|perf`

### Backends
- `--gfx=<backend>` (canonical gfx backend selector)
- `--sys.<subsystem>=<backend>` (canonical subsystem override)
- `--platform=<backend>` (deprecated alias for platform/dsys backend)

### Tick / determinism
- `--tickrate=<ups>`
- `--lockstep-strict=0|1`
- `--deterministic-test`

### Replay
- `--record-replay=<path>`
- `--play-replay=<path>`
- `--replay-strict-content=0|1`

### Save / load
- `--save=<path>`
- `--load=<path>`

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

