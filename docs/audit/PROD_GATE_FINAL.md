Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: release-pinned standalone product boot gate summary

# PROD Gate Final

Fingerprint: `f50aae97b9691c219597f9aef9a2c22289c1fca9345dbb0f192f8f4e2ffc6d6e`

## Pass/Fail By Product

| Product | Descriptor | Help | Compat | Validate | IPC |
| --- | --- | --- | --- | --- | --- |
| `client` | `pass` | `pass` | `pass` | `pass` | `pass` |
| `engine` | `pass` | `pass` | `pass` | `pass` | `n/a` |
| `game` | `pass` | `pass` | `pass` | `pass` | `n/a` |
| `launcher` | `pass` | `pass` | `pass` | `pass` | `pass` |
| `server` | `pass` | `pass` | `pass` | `pass` | `pass` |
| `setup` | `pass` | `pass` | `pass` | `pass` | `pass` |
| `tool.attach_console_stub` | `pass` | `pass` | `pass` | `pass` | `pass` |

## Mode Selections Observed

| Product | Portable TTY | Portable GUI | Installed TTY | Installed GUI |
| --- | --- | --- | --- | --- |
| `client` | `tui` | `rendered` | `tui` | `rendered` |
| `engine` | `cli` | `cli` | `cli` | `cli` |
| `game` | `tui` | `cli` | `tui` | `cli` |
| `launcher` | `tui` | `cli` | `tui` | `cli` |
| `server` | `tui` | `cli` | `tui` | `cli` |
| `setup` | `tui` | `cli` | `tui` | `cli` |
| `tool.attach_console_stub` | `tui` | `cli` | `tui` | `cli` |

## Degradations Observed

- `game` `installed` `gui` degraded by `1` step(s).
- `game` `portable` `gui` degraded by `1` step(s).
- `launcher` `installed` `gui` degraded by `2` step(s).
- `launcher` `portable` `gui` degraded by `2` step(s).
- `server` `installed` `gui` degraded by `1` step(s).
- `server` `portable` `gui` degraded by `1` step(s).
- `setup` `installed` `gui` degraded by `2` step(s).
- `setup` `portable` `gui` degraded by `2` step(s).
- `tool.attach_console_stub` `installed` `gui` degraded by `1` step(s).
- `tool.attach_console_stub` `portable` `gui` degraded by `1` step(s).

## Readiness

- Ready for IPC-UNIFY-0 and supervisor hardening when this gate remains green alongside RepoX, AuditX, and TestX.
