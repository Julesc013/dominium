Status: CANONICAL
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: RELEASE/MVP
Replacement Target: release-pinned standalone product boot contract

# Product Boot Matrix

This matrix defines the minimum standalone product behaviors required for `PROD-GATE-0`.

## Matrix

| Product | Portable Invocation | Installed Invocation | TTY Expected Mode | GUI Expected Mode | Required Commands | Expected Refusal Codes |
| --- | --- | --- | --- | --- | --- | --- |
| `Client` | `client` | `client (installed registry discovery)` | `tui` | `rendered` | `--descriptor<br>help<br>compat-status<br>validate --all --profile FAST` | `refusal.install.not_found<br>refusal.compat.feature_disabled` |
| `Engine` | `engine` | `engine (installed registry discovery)` | `cli` | `cli` | `--descriptor<br>help<br>compat-status<br>validate --all --profile FAST` | `refusal.install.not_found<br>refusal.compat.feature_disabled` |
| `Game` | `game` | `game (installed registry discovery)` | `tui` | `cli` | `--descriptor<br>help<br>compat-status<br>validate --all --profile FAST` | `refusal.install.not_found<br>refusal.compat.feature_disabled` |
| `Launcher` | `launcher` | `launcher (installed registry discovery)` | `tui` | `cli` | `--descriptor<br>help<br>compat-status<br>validate --all --profile FAST` | `refusal.install.not_found<br>refusal.compat.feature_disabled` |
| `Server` | `server` | `server (installed registry discovery)` | `tui` | `cli` | `--descriptor<br>help<br>compat-status<br>validate --all --profile FAST` | `refusal.install.not_found<br>refusal.compat.feature_disabled` |
| `Setup` | `setup` | `setup (installed registry discovery)` | `tui` | `cli` | `--descriptor<br>help<br>compat-status<br>validate --all --profile FAST` | `refusal.install.not_found<br>refusal.compat.feature_disabled` |
| `Tools` | `tool_attach_console_stub` | `tool_attach_console_stub (installed registry discovery)` | `tui` | `cli` | `--descriptor<br>help<br>compat-status<br>validate --all --profile FAST` | `refusal.install.not_found<br>refusal.compat.feature_disabled` |

## Notes

- Product mode selection must route through `appshell/ui_mode_selector.py` with platform capabilities sourced from `engine/platform/platform_probe.py`.
- `compat-status` must expose both `mode_selection` and `install_discovery` for every product.
- Portable runs resolve from `install.manifest.json` adjacent to the product executable.
- Installed runs resolve through `install_registry.json` without bypassing virtual paths, negotiation, or validation surfaces.
