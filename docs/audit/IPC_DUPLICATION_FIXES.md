Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# IPC Duplication Fixes
This report records the canonical IPC surfaces and any remaining duplicate or legacy IPC logic.

## Canonical Stack

| Surface | Consumer | Canonical Target | Notes |
| --- | --- | --- | --- |
| Console attach command | `src/appshell/commands/command_engine.py` | `src/appshell/ipc/ipc_client.py` | All console attach requests route through attach_ipc_endpoint/query_ipc_status/query_ipc_log_events/run_ipc_console_command. |
| TUI multiplex | `src/appshell/tui/tui_engine.py` | `src/appshell/ipc/ipc_client.py` | TUI session tabs attach and refresh through the shared IPC client helpers. |
| Supervisor attach | `src/appshell/supervisor/supervisor_engine.py` | `src/appshell/ipc/ipc_client.py` | Supervisor attach and log merge flows reuse the same IPC client and negotiation path. |
| Endpoint listener | `src/appshell/ipc/ipc_endpoint_server.py` | `src/appshell/ipc/ipc_transport.py` | Endpoint server opens the canonical listener and emits deterministic frames only after handshake success. |

## Remaining Duplicate Or Legacy Paths

- None. Supervisor, command-engine attach, and TUI multiplexing all route through `src/appshell/ipc/ipc_client.py`.
