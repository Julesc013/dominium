Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: APPSHELL
Replacement Target: release-pinned platform adapter contracts and install discovery guarantees

# Platform Renderer Matrix

Fingerprint: `ea0e7a7023a8efffceac1c527f2ec769da2a41db7cc5e09900a3daa9e5cd4e78`

## Declared vs Repo-Supported Matrix

| Platform | Tier | Declared UI | Client Supported Modes | Client Available Modes (GUI) | Launcher Available Modes (GUI) | Server Available Modes (TTY) | Renderer Backends | IPC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `platform.win9x` | `subset` | `native=yes` `rendered=no` `tui=yes` `cli=yes` | `tui`, `cli` | `cli` | `cli` | `tui`, `cli` | `null`, `software` | `none` |
| `platform.winnt` | `full` | `native=yes` `rendered=yes` `tui=yes` `cli=yes` | `rendered`, `tui`, `cli` | `rendered`, `cli` | `cli` | `tui`, `cli` | `null`, `software`, `opengl` | `named_pipe` |
| `platform.macos_classic` | `subset` | `native=yes` `rendered=no` `tui=no` `cli=yes` | `cli` | `cli` | `cli` | `cli` | `null`, `software` | `none` |
| `platform.macos_cocoa` | `full` | `native=yes` `rendered=yes` `tui=yes` `cli=yes` | `rendered`, `tui`, `cli` | `rendered`, `cli` | `cli` | `tui`, `cli` | `null`, `software`, `opengl` | `none` |
| `platform.linux_gtk` | `full` | `native=yes` `rendered=yes` `tui=yes` `cli=yes` | `rendered`, `tui`, `cli` | `rendered`, `cli` | `cli` | `tui`, `cli` | `null`, `software`, `opengl` | `none` |
| `platform.posix_min` | `subset` | `native=no` `rendered=no` `tui=yes` `cli=yes` | `tui`, `cli` | `cli` | `cli` | `tui`, `cli` | `null` | `none` |
| `platform.sdl_stub` | `future_stub` | `native=no` `rendered=yes` `tui=yes` `cli=yes` | `rendered`, `tui`, `cli` | `rendered`, `cli` | `cli` | `tui`, `cli` | `null`, `software`, `opengl` | `none` |
