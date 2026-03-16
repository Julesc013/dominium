Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/appshell/APPSHELL_CONSTITUTION.md`, `docs/appshell/IPC_ATTACH_CONSOLES.md`, `docs/appshell/LOGGING_AND_TRACING.md`, `docs/packs/PACK_VERIFICATION_PIPELINE.md`, and `docs/compat/NEGOTIATION_HANDSHAKES.md`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Supervisor Model

## Purpose

APPSHELL-6 defines deterministic multi-process supervision for launcher-driven
offline sessions, headless server runs, and future tool attachments.

## Responsibilities

The AppShell supervisor is the launcher-owned orchestration surface for portable offline runs. It must:

1. validate environment inputs before boot:
   - semantic contracts pinned
   - packs verified
   - pack lock present
2. spawn processes deterministically:
   - server
   - client
   - tool hosts later
3. supervise process health:
   - monitor exit codes on deterministic refresh boundaries
   - restart only if policy allows
4. auto-attach IPC:
   - logs
   - console
   - status
5. emit a deterministic run manifest for proofs and diagnostics.

Supervisor ordering must remain deterministic across platforms and thread counts.

## Deterministic Process Args

Supervisor args are constructed from:

- SessionSpec template
- seed
- profile bundle
- pack lock
- contract bundle hash
- mod policy id
- overlay conflict policy id

Argument ordering must be stable and canonical. No host-derived random paths or wall-clock values are permitted.

## Policies

`supervisor.policy.default`
- `max_restarts = 0`
- `restart_backoff_iterations = 0`
- `readiness_poll_iterations = 6`
- `auto_attach_ipc = true`
- no silent restart

`supervisor.policy.lab`
- bounded restart allowance for local experimentation
- `restart_backoff_iterations = 1`
- `readiness_poll_iterations = 8`
- still uses deterministic restart ordering and preserved args

## Startup

`supervisor_start(run_spec)` performs:

1. PACK-COMPAT verification
2. deterministic child arg canonicalization
3. server spawn
4. bounded polling iterations for IPC-ready negotiated state
5. client spawn if topology requires it
6. automatic IPC attach for logs and console surfaces
7. run manifest emission

## Shutdown

Graceful shutdown order is fixed:

1. client
2. server

The supervisor never uses wall-clock timeouts. It uses bounded polling iterations only.

## Log Aggregation

The unified supervisor log view merges child streams by:

1. `source_product_id`
2. `seq_no`
3. `endpoint_id`
4. `event_id`

This merge order is stable and must not depend on arrival timing.

## Enforcement Notes

- Restart policy evaluation is deterministic and profile-driven.
- Restart backoff is measured in deterministic refresh iterations only.
- Log aggregation must remain deterministic and bounded.
- Supervisor attach and restart behavior must continue to use negotiated IPC and
  deterministic refusal paths.
