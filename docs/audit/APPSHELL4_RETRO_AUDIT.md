Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# APPSHELL-4 Retro Audit

## Scope

Audit target:

- AppShell bootstrap, commands, logging, and TUI surfaces
- existing client/server loopback negotiation flow
- local transport options for portable IPC
- attachable console/session seams already present in APPSHELL-3

## Findings

### 1. Loopback negotiation plumbing already exists and is reusable

`src/server/net/loopback_transport.py` already performs deterministic descriptor
exchange, CAP-NEG negotiation, acknowledgement, and read-only enforcement for
client/server loopback.

Implication:

- APPSHELL-4 should reuse the CAP-NEG handshake helpers
- AppShell IPC must not invent a separate ad hoc negotiation surface

### 2. AppShell already has the main building blocks for attachable consoles

The following shared surfaces already exist:

- registry-backed command dispatch in `src/appshell/commands/command_engine.py`
- structured log rings in `src/appshell/logging/log_engine.py`
- multiplexed logical console sessions in `src/appshell/tui/tui_engine.py`

Implication:

- IPC attach can layer on top of command dispatch and log rings
- TUI multiplexing should extend the existing session-tab model instead of
  replacing it

### 3. There is no shared local IPC transport yet

The repository has deterministic in-process loopback helpers under
`src/net/transport/loopback.py`, but there is no AppShell-level local IPC
transport usable across processes.

Implication:

- APPSHELL-4 needs a shared local socket transport
- Windows and Unix must be handled through a deterministic abstraction

### 4. Current shell arguments do not expose IPC lifecycle controls

`src/appshell/args_parser.py` supports mode, descriptor, version, and TUI
layout flags, but not endpoint lifecycle flags such as `--ipc on`.

Implication:

- AppShell bootstrap needs explicit IPC on/off controls
- endpoint identity must be explicit and deterministic per product/session

### 5. TUI sessions are already modeled as logical tabs but have no remote attach path

APPSHELL-3 already models console sessions as logical tabs, with deterministic
ordering and active-session focus rules, but every session is still local.

Implication:

- APPSHELL-4 can add remote endpoint sessions without changing the TUI layout
  model
- remote attach state must remain derived from negotiated endpoint/session data

## Audit Conclusion

APPSHELL-4 can be implemented as a shared AppShell IPC layer that:

- reuses CAP-NEG negotiation
- reuses AppShell commands/logging/TUI session models
- introduces deterministic local framing and discovery
- preserves read-only enforcement and avoids privilege escalation
