Status: CANONICAL
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: APPSHELL
Replacement Target: release-pinned standalone shell and product UI bootstrap contract

# UI Mode Resolution

AppShell owns deterministic product UI selection before product bootstrap, pack validation handoff, or IPC startup.

## Decision Tree

1. Parse explicit `--mode` or supported legacy `--ui` migration.
2. Probe presentation-only host capabilities through `src/platform/platform_probe.py`.
3. If an explicit mode was requested, honor it when available; otherwise degrade through the CAP-NEG fallback map.
4. Without an explicit mode, use the product policy order for the detected context:
   - `tty`: prefer interactive console surfaces.
   - `gui`: prefer GUI surfaces when no TTY is attached.
   - `headless`: prefer deterministic CLI/non-interactive fallback.
5. Emit structured `appshell.mode.selected` and `appshell.mode.degraded` events when applicable.

## Detection Methods

- TTY: `sys.std*.isatty()`
- Windows GUI heuristic: console-window presence via `GetConsoleWindow`
- POSIX GUI heuristic: `DISPLAY` / `WAYLAND_DISPLAY`
- macOS GUI heuristic: Cocoa import or bundle env hint
- TUI availability: `curses` import plus TTY context
- Rendered availability: client render host markers plus GUI context
- OS-native availability: platform adapter markers plus GUI context

## Product Policies

| Product | GUI Order | TTY Order | Headless Order | Legacy Explicit Modes |
| --- | --- | --- | --- | --- |
| `client` | `rendered -> os_native -> tui -> cli` | `tui -> cli -> rendered` | `cli` | `none` |
| `engine` | `cli -> tui` | `cli -> tui` | `cli -> headless` | `headless` |
| `game` | `tui -> cli` | `tui -> cli` | `cli` | `none` |
| `launcher` | `os_native -> tui -> cli` | `tui -> cli` | `cli` | `none` |
| `server` | `tui -> cli` | `tui -> cli` | `cli -> headless` | `headless` |
| `setup` | `os_native -> tui -> cli` | `tui -> cli` | `cli` | `none` |
| `tool.attach_console_stub` | `tui -> cli` | `tui -> cli` | `cli` | `none` |

## Notes

- `client` prefers `rendered` in GUI contexts, but TTY contexts prefer `tui` first.
- `setup` and `launcher` prefer `os_native` only when a platform adapter exists; otherwise they degrade to `tui` or `cli`.
- `server` and `engine` keep `headless` only as an explicit legacy/non-interactive mode.
- UI mode selection is presentation-only and must not affect authoritative truth or simulation semantics.
