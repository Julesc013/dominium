Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# Local Singleplayer Model

## Purpose

SERVER-MVP-1 defines the MVP local singleplayer orchestration surface.

Local singleplayer is still server authoritative.

- client is presentation and perception only
- local server owns the authoritative TruthModel
- session/pack/contract validation still happens on server boot

## Lifecycle

The deterministic local singleplayer lifecycle is:

1. materialize or load the pinned `SessionSpec`
2. build deterministic server spawn arguments
3. gate local authority by server profile
4. boot local authority
5. wait for ready handshake through bounded polling iterations
6. attach local client through deterministic loopback

On crash or boot failure:

- capture the last deterministic logs available
- emit a local diag stub bundle
- expose restart as a fresh controller start using the same pinned session inputs

## Process Preference and Current Transport Reality

SERVER-MVP-1 prefers process spawn for realism and future APPSHELL parity.

However, the current MVP loopback transport is process-local in-memory state.

Therefore:

- deterministic process spawn arguments are built and supervised now
- the active connectable authority path is `inproc_loopback_stub`
- this is the explicit handoff point for future IPC/socket transport replacement

No hidden fallback is permitted.
The in-proc path is an intentional documented MVP limitation.

## Control Channel Stub

The local client may issue bounded loopback control requests:

- `status`
- `save_snapshot`

The server may stream deterministic console/log events tagged by canonical tick.

This is not a general IPC protocol.
It is a loopback control stub only.

## Deterministic Readiness

Ready detection must not use wall-clock timeouts.

SERVER-MVP-1 uses bounded polling iterations against the deterministic loopback handshake:

- send client hello
- poll `accept_loopback_connection`
- either:
  - complete within the bounded iteration count
  - refuse with remediation and diag stub

## Profile Gate

Local authority spawning is profile-driven.

For v0.0.0:

- allowed:
  - `server.profile.private_relaxed`
- refused:
  - strict/ranked profiles such as `server.profile.rank_strict`

Stable refusal code:

- `refusal.client.local_authority_forbidden`

## Refusal Codes

- `refusal.client.local_authority_forbidden`
- `refusal.local_server.ready_unreached`
- `refusal.local_server.crashed`
- `refusal.session.contract_mismatch`
- `refusal.session.pack_lock_mismatch`

## Scope Limits

SERVER-MVP-1 does not provide:

- full APPSHELL supervision
- full IPC protocol
- remote server discovery
- matchmaking
- wall-clock driven backoff or retry loops
