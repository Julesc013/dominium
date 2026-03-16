Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DIST
Replacement Target: DIST-5 UX polish and archive support notes

# Supported Platforms v0.0.0 Mock

This matrix records the shipped UI layers per platform family and the deterministic fallback policy for forcing AppShell modes.

## Platform Support

| Platform | Support Tier | Built In DIST-4 | UI Layers | Notes |
| --- | --- | --- | --- | --- |
| `platform.linux_gtk` | `full` | `no` | `os_native, rendered, tui, cli` | `not built in current matrix run` |
| `platform.macos_classic` | `subset` | `no` | `os_native, cli` | `not built in current matrix run` |
| `platform.macos_cocoa` | `full` | `no` | `os_native, rendered, tui, cli` | `not built in current matrix run` |
| `platform.posix_min` | `subset` | `no` | `tui, cli` | `not built in current matrix run` |
| `platform.sdl_stub` | `future_stub` | `no` | `rendered, tui, cli` | `not built in current matrix run` |
| `platform.win9x` | `subset` | `no` | `os_native, tui, cli` | `not built in current matrix run` |
| `platform.winnt` | `full` | `yes` | `os_native, rendered, tui, cli` | `built from `win64`` |

## Known Disabled Capabilities

- OS-native GUI adapters are only selected when the platform row and shipped adapter markers both declare support.
- Rendered UI is currently only expected for client bundles that ship the rendered host markers.
- TUI is preferred for interactive server, engine, and game contexts when available; CLI remains the universal fallback.

## Forcing a Mode

- `bin/client compat-status --mode rendered`
- `bin/setup compat-status --mode os_native`
- `bin/server compat-status --mode tui`
- `bin/launcher compat-status --mode cli`
