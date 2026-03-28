Status: CANONICAL
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: APPSHELL
Replacement Target: release-pinned standalone product command reference after convergence

# Flag Migration

Legacy boot flags remain supported, but AppShell owns the canonical entry surface.

| Product | Legacy Flag | Canonical AppShell Flag | Status |
| --- | --- | --- | --- |
| `client` | `--ui gui|cli` | `--mode rendered|cli` | `supported_with_warning` |
| `server` | `--ui headless|cli` | `--mode headless|cli` | `supported_with_warning` |
| `*` | `--portable` | `--install-root <portable adjacency root>` | `supported_with_warning` |
| `*` | `--no-gui` | `--mode tui|cli` | `supported_with_warning` |

## Notes

- `client` and `server` continue to accept legacy `--ui` values, but AppShell resolves them as `--mode` before product bootstrap.
- `--portable` remains accepted as a convergence shim. When an adjacent `install.manifest.json` is present, AppShell translates it into an explicit `--install-root` selection before install discovery runs.
- `--no-gui` remains accepted as a convergence shim. AppShell translates it into a deterministic non-GUI mode request: `tui` when supported, otherwise `cli`.
- Default mode selection is now centralized in `appshell/ui_mode_selector.py` and follows the product policy registry plus deterministic platform probing.
- `headless` remains an explicit legacy/non-interactive mode for governed server and engine surfaces; it is not part of the default interactive ladder.
- Existing product-domain flags such as setup `--ui-mode` remain product arguments and are not AppShell shell-mode aliases.
- Deprecated legacy flags emit a structured AppShell warning event before product bootstrap.
