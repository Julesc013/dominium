Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# TUI Mode

TUI is a runtime feature for client and tools. Tests remain CLI-only and do not
depend on TUI paths.

## Entry points
- `client --ui=tui` (or `--tui`)
- `tools --ui=tui` (or `--tui`)

Environment defaults:
- `DOM_UI=tui` (or `DOM_UI_MODE=tui`) when no CLI flag is provided

Optional flags:
- `--deterministic` / `--interactive`
- `--frame-cap-ms <ms>` (interactive only; `0` disables)

## Input and rendering
- Terminal input is normalized into the DSYS event queue using
  `dsys_inject_event()`.
- The TUI widget tree is rendered via `domino/tui` and `dsys_term`.
- Key bindings: arrow keys for navigation, `Enter` for activation, `Q` to quit.

## Platform support
- POSIX: raw terminal mode + ANSI output.
- Windows: console API (cursor positioning + input events).

## CLI-only isolation
`--smoke`/`--selftest` paths never enter TUI and remain deterministic.