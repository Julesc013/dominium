Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# APPSHELL Logging Baseline

## Scope

APPSHELL-2 adds the shared log engine, deterministic sink handling, and the
minimal offline diagnostic snapshot bundle.

## Categories

The baseline categories are:

- `appshell`
- `compat`
- `packs`
- `worldgen`
- `server`
- `client`
- `ui`
- `tool`
- `diag`
- `refusal`

## Message Keys

The baseline registry includes keys for:

- AppShell bootstrap and command dispatch
- refusal emission
- compatibility negotiation outcomes
- pack verification and pack-lock generation
- refinement request summaries
- server listener/connection/control/tick/proof-anchor events
- diagnostic snapshot emission

## Sink Configuration

APPSHELL-2 baseline sinks:

- console sink to `stderr`
- JSON-lines file sink
- bounded in-memory ring sink

The shared log engine truncates the run-local file sink on startup so each
process run owns a deterministic file artifact.

## Diagnostics

`diag snapshot` writes:

- `diag_manifest.json`
- `endpoint_descriptor.json`
- `session_spec.json`
- `pack_lock.json`
- `log_events.jsonl`
- `proof_anchors.json`
- `replay_instructions.txt`

## Readiness

This baseline is sufficient for:

- APPSHELL-3 TUI event surfaces
- later IPC log streaming
- DIAG-0 richer offline repro bundles
