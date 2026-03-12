Status: CANONICAL
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: APPSHELL
Replacement Target: release-pinned standalone product command reference after convergence

# Flag Migration

Legacy boot flags remain supported, but AppShell owns the canonical entry surface.

| Product | Legacy Flag | Canonical AppShell Flag | Status |
| --- | --- | --- | --- |
| `client` | `--ui gui|cli` | `--mode rendered|cli` | `supported_with_warning` |
| `server` | `--ui headless|cli` | `--mode headless|cli` | `supported_with_warning` |

## Notes

- `client` and `server` continue to accept legacy `--ui` values, but AppShell resolves them as `--mode` before product bootstrap.
- Existing product-domain flags such as setup `--ui-mode` remain product arguments and are not AppShell shell-mode aliases.
- Deprecated legacy flags emit a structured AppShell warning event before product bootstrap.
