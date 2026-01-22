# GUI Mode

GUI is an optional runtime layer. All TESTX paths remain CLI-only.

## Client flags
- `--ui=gui|tui|none` selects the shell:
  - `gui` maps to windowed mode.
  - `tui` starts the terminal UI.
  - `none` forces CLI-only.
- Legacy flags remain supported: `--windowed`, `--tui`, `--borderless`,
  `--fullscreen`, `--width`, `--height`.

## Behavior
- Windowed mode uses `dsys_window_*` for lifecycle and `d_gfx_*` for rendering.
- No packs are required; a procedural debug overlay is drawn via `d_gfx`.
- `B` toggles windowed <-> borderless at runtime (best-effort).
- Explicit renderer selection fails loudly if unavailable; auto selection logs
  the chosen backend and reason.
