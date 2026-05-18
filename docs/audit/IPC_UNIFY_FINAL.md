Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# IPC Unify Final
## Canonical Stack

- Transport: `runtime/appshell/ipc/ipc_transport.py`
- Handshake: `compat/handshake/handshake_engine.py`
- Attach client: `runtime/appshell/ipc/ipc_client.py`
- Endpoint server: `runtime/appshell/ipc/ipc_endpoint_server.py`
- Consumers: `runtime/appshell/commands/command_engine.py`, `runtime/appshell/tui/tui_engine.py`, and `runtime/appshell/supervisor/supervisor_engine.py`

## Removed Duplicate IPC Paths

- No duplicate runtime transport or attach protocol remains outside the canonical AppShell IPC stack.
- Test-only raw frame access remains confined to `tools/appshell/appshell4_probe.py`.

## Attach Discipline Summary

- Unnegotiated attach refusal: `refusal.connection.no_negotiation`
- Negotiation record hash: `56e4e2b4cf76e62533f86a6ef51e05bbcbe3722eca0205a1dd381b4e882a0f17`
- Replay result: `complete`
- VROOT discovery result: `complete`

## Runtime Verification

- Attach probe result: `complete`
- Cross-platform IPC hash: `ec7a3b39c953388a85e77d32545edc4aeb611f698b9bbb734a39700eaa5f8ec8`
- Replay mismatches: `none`
- Descriptor file path: `C:/Inbox/Git Repos/dominium/build/appshell/ipc_unify/store/runtime/endpoints/ipc.server.session.ipc_unify.vroot.json`

## Readiness

- Ready for `SUPERVISOR-HARDEN-0` once the broader repo strict lanes are rerun.
- Ready for portable and installed attach flows through `VROOT_IPC`.

## Violations

- None.
