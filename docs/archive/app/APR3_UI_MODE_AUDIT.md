# ARCHIVED: APR3 UI Mode Audit

Archived: point-in-time UI audit.
Reason: APR audit snapshot; current UI contracts supersede it.
Superseded by:
- `docs/app/UI_MODES.md`
- `docs/app/GUI_MODE.md`
- `docs/app/TUI_MODE.md`
Still useful: background on early UI mode inventory.

# APR3 UI Mode Audit

## Summary
This audit captures current UI mode support and inconsistencies across products before APR3 changes.

## Client (client/app/main_client.c)
- CLI modes: `--ui=gui|tui|none`, `--tui`, and window flags (`--windowed`, `--borderless`, `--fullscreen`).
- TUI: built-in Domino TUI via `d_tui_*`, optional and bypassed in smoke/selftest paths.
- GUI: renderer-driven windowed shell via `dsys` + `d_gfx`.
- Gaps: mode parsing is product-specific; no shared UI mode contract or app-runtime utilities.

## Server (server/app/main_server.c)
- CLI only; no `--ui` flag or TUI/GUI modes.
- Headless path is the only supported runtime shell.
- Gaps: add `--ui=none|tui|gui` plumbing and optional TUI/GUI stubs.

## Launcher (launcher/cli/launcher_cli_main.c)
- CLI only; no `--ui` flag.
- Separate executables exist: `launcher_gui` and `launcher_tui` (stubbed), not wired to CLI.
- CLI uses `dsys` only for `capabilities` command; smoke/status remain CLI-only.
- Gaps: unify mode selection in main CLI and expose TUI/GUI via the same entrypoint.

## Setup (setup/cli/setup_cli_main.c)
- CLI only; no `--ui` flag.
- Separate executables exist: `setup_gui` and `setup_tui` (stubbed), not wired to CLI.
- CLI paths are pack-agnostic and deterministic.
- Gaps: unify mode selection in main CLI and expose TUI/GUI via the same entrypoint.

## Tools (tools/tools_host_main.c)
- CLI + `--tui` flag; no `--ui` flag or GUI mode.
- TUI uses Domino TUI and `dsys` event queue when selected.
- Gaps: add `--ui=none|tui|gui` and GUI stub path.

## Cross-product consistency issues
- UI mode flags are inconsistent (`--ui` only in client; `--tui` only in client/tools).
- Separate GUI/TUI executables are not reachable via CLI mode selection.
- No shared application-runtime utilities for UI mode parsing, timing/loop helpers, build-info formatting, or capability report formatting.

## Optionality and hidden dependencies
- CLI smoke/selftest paths remain independent of GUI/TUI across all products.
- `capabilities` in launcher relies on `dsys_init`; failure is handled and does not affect other CLI paths.
- GUI/TUI frontends are currently isolated in separate executables (launcher/setup), not linked into CLI paths.
