Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# APPSHELL IPC Baseline

## Endpoint Lifecycle

APPSHELL-4 endpoints are optional per process and are enabled through
`--ipc on`.

Each endpoint:

- publishes a deterministic entry in `VROOT_IPC/ipc_endpoints.json`
- writes a deterministic descriptor file in `VROOT_IPC/endpoints/<endpoint_id>.json`
- exposes negotiation, console, log, and status channels
- removes its manifest entry on shutdown

## Attach / Detach Protocol

Attach flow:

1. deterministic discovery
2. CAP-NEG handshake
3. `NegotiationRecord` acceptance/refusal
4. request/response access to status, console, and logs

Detach flow:

- remove the local logical session binding
- keep remote product state unchanged

## TUI Multiplex

Attached endpoints are surfaced as logical console tabs.

Baseline behavior:

- deterministic tab ordering
- remote command execution through the shared command engine
- remote log polling merged into the logs panel

## Read-Only And Security

If negotiation chooses `compat.read_only`, APPSHELL-4 restricts the attached
session to a read-only command allowlist and logs the downgraded mode.

No APPSHELL-4 attach path can bypass negotiation or escalate privileges.

## Readiness

This baseline is sufficient for:

- APPSHELL-6 supervisor-driven multi-process orchestration
- DIAG-0 richer repro bundles including attach transcripts
- future remote/localhost transport expansion without changing the shell
  semantics
