Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Entrypoint Map

Status: `DERIVED`
Source: `tools/review/tool_repo_inventory.py`

| Product | Executables | Source | AppShell | UI Adapter | IPC | Supervisor |
| --- | --- | --- | --- | --- | --- | --- |
| `client` | `client`, `dominium_client` | `tools/mvp/runtime_entry.py` | `yes` | `yes` | `yes` | `no` |
| `engine` | `engine` | `tools/appshell/product_stub_cli.py` | `yes` | `yes` | `no` | `no` |
| `game` | `game` | `tools/appshell/product_stub_cli.py` | `yes` | `yes` | `no` | `no` |
| `launcher` | `launcher` | `tools/launcher/launch.py` | `yes` | `yes` | `yes` | `yes` |
| `server` | `dominium_server`, `server` | `src/server/server_main.py` | `yes` | `yes` | `yes` | `no` |
| `setup` | `setup` | `tools/setup/setup_cli.py` | `yes` | `yes` | `yes` | `no` |
| `tool.attach_console_stub` | `tool_attach_console_stub` | `tools/appshell/product_stub_cli.py` | `yes` | `yes` | `yes` | `no` |

## AppShell Bypasses

- None detected.
