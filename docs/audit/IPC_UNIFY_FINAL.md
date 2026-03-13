Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# IPC Unify Final
## Canonical Stack

- Transport: `src/appshell/ipc/ipc_transport.py`
- Handshake: `src/compat/handshake/handshake_engine.py`
- Attach client: `src/appshell/ipc/ipc_client.py`
- Endpoint server: `src/appshell/ipc/ipc_endpoint_server.py`
- Consumers: `src/appshell/commands/command_engine.py`, `src/appshell/tui/tui_engine.py`, and `src/appshell/supervisor/supervisor_engine.py`

## Removed Duplicate IPC Paths

- No duplicate runtime transport or attach protocol remains outside the canonical AppShell IPC stack.
- Test-only raw frame access remains confined to `tools/appshell/appshell4_probe.py`.

## Attach Discipline Summary

- Unnegotiated attach refusal: `refusal.connection.no_negotiation`
- Negotiation record hash: `d7ff28f88830e885090d8c3dd10f731eee4c5e04735569e2e54e49e500ed0892`
- Replay result: `complete`
- VROOT discovery result: `complete`

## Runtime Verification

- Attach probe result: `complete`
- Cross-platform IPC hash: `cc7a2e076ee5b107e607af4efd53fe1e7145510ceb106c595112d1e823f6b422`
- Replay mismatches: `none`
- Descriptor file path: `D:/Projects/Dominium/dominium/build/appshell/ipc_unify/store/runtime/endpoints/ipc.server.session.ipc_unify.vroot.json`

## Readiness

- Ready for `SUPERVISOR-HARDEN-0` once the broader repo strict lanes are rerun.
- Ready for portable and installed attach flows through `VROOT_IPC`.

## Violations

- None.
