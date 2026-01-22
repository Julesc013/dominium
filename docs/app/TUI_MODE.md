# TUI Mode

TUI is a runtime feature for client and tools. Tests remain CLI-only and do not
depend on TUI paths.

## Entry points
- `client --tui`
- `tools --tui`

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
