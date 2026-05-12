Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# IPC Surface Map
This inventory lists the real IPC surfaces in the repository and classifies them against the canonical AppShell IPC stack.

## Canonical Surfaces

| Path | Surface | Classification | Notes |
| --- | --- | --- | --- |
| `compat/handshake/handshake_engine.py` | handshake | canonical | Single CAP-NEG handshake message builder for IPC attach and session begin. |
| `runtime/appshell/commands/command_engine.py` | command_entrypoint | canonical | AppShell console attach command routes through the canonical IPC client. |
| `runtime/appshell/ipc/ipc_client.py` | attach_client | canonical | Canonical attach/discovery/status/log/console client surface. |
| `runtime/appshell/ipc/ipc_endpoint_server.py` | endpoint_server | canonical | Canonical negotiated attach server and channel dispatcher. |
| `runtime/appshell/ipc/ipc_transport.py` | transport | canonical | Single transport abstraction, framing, manifest, and descriptor-file discovery. |
| `runtime/appshell/supervisor/supervisor_engine.py` | supervisor_consumer | canonical | Supervisor uses the canonical attach/status/log/console IPC client. |
| `runtime/appshell/tui/tui_engine.py` | tui_consumer | canonical | TUI multiplexing uses the canonical attach/status/log/console IPC client. |
| `tools/appshell/appshell4_probe.py` | probe | canonical | Test-only deterministic raw-frame probe for attach, sequencing, and replay verification. |

## Direct Socket Users

| Path | Classification | Reason | Hits |
| --- | --- | --- | --- |

## Low-Level IPC Primitive Users

| Path | Classification | Reason | Hits |
| --- | --- | --- | --- |
| `tools/appshell/appshell4_probe.py` | canonical | test_only_probe | `connect_ipc_client(`, `send_frame(`, `recv_frame(` |

## Canonical Consumer Bindings

| Surface | Consumer | Canonical Target | Notes |
| --- | --- | --- | --- |
| Console attach command | `runtime/appshell/commands/command_engine.py` | `runtime/appshell/ipc/ipc_client.py` | All console attach requests route through attach_ipc_endpoint/query_ipc_status/query_ipc_log_events/run_ipc_console_command. |
| TUI multiplex | `runtime/appshell/tui/tui_engine.py` | `runtime/appshell/ipc/ipc_client.py` | TUI session tabs attach and refresh through the shared IPC client helpers. |
| Supervisor attach | `runtime/appshell/supervisor/supervisor_engine.py` | `runtime/appshell/ipc/ipc_client.py` | Supervisor attach and log merge flows reuse the same IPC client and negotiation path. |
| Endpoint listener | `runtime/appshell/ipc/ipc_endpoint_server.py` | `runtime/appshell/ipc/ipc_transport.py` | Endpoint server opens the canonical listener and emits deterministic frames only after handshake success. |
