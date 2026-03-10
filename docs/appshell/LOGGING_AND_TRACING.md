Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, and `docs/appshell/APPSHELL_CONSTITUTION.md`.

# Logging And Tracing

## Purpose

APPSHELL-2 defines deterministic structured logging and minimal offline
diagnostics for Dominium products.

Logging and tracing are presentation and diagnostics surfaces only.
They must never mutate TruthModel, establish law, or influence simulation.

## Log Event Structure

Every AppShell log event uses the same shape:

- `event_id`
- `product_id`
- `build_id`
- `session_id` optional
- `tick` optional canonical tick
- `severity`
- `category`
- `message_key`
- `params`
- `host_meta`
- `deterministic_fingerprint`
- `extensions`

Rules:

- `event_id` is a deterministic sequence number local to the process run
- `message_key` is a stable registry-backed identifier
- `params` is a typed map serialized in sorted-key order
- `host_meta` may contain host timestamps or transport metadata, but those fields
  are non-authoritative and must not influence truth, proofs, or negotiation

## Ordering

Log emission order is deterministic for identical command and process sequences.

Rules:

- events are ordered by their local sequence number
- file sinks flush one event per line in emission order
- ring buffers preserve the last `N` events in emission order
- log serialization must not depend on Python dict iteration order

## Redaction

Log payloads are observable surfaces.

Rules:

- redaction is controlled by epistemic profile and authority context
- redaction may remove or replace parameter values
- redaction must not reorder fields or alter the deterministic structure of the
  event

APPSHELL-2 establishes the contract surface and baseline behavior. More granular
policy profiles may refine redaction later.

## Sinks

The canonical AppShell sink families are:

- `sink.console`
- `sink.file`
- `sink.memory_ring`

Rules:

- console sinks are for operator visibility only
- file sinks are structured offline artifacts
- memory rings are bounded and exist to support diagnostics bundles and later IPC
  streaming

## Diagnostics

`diag snapshot` writes a deterministic offline diagnostic bundle containing:

- endpoint descriptor
- session spec when available
- pack lock when available
- contract bundle hash
- bounded recent log events
- bounded recent proof anchors when available
- replay instructions

This is a shell-level diagnostic surface and is not a substitute for canonical
proof or replay artifacts.

## Non-Goals

APPSHELL-2 does not:

- make logs authoritative
- require external logging services
- require network access
- define full DIAG-0 repro bundles
- define TUI multiplexing or IPC log streaming transport details

## Readiness

APPSHELL-2 establishes the structured logging baseline required for:

- APPSHELL-3 TUI panel/event views
- APPSHELL-4 attach and multiplex surfaces
- DIAG-0 full offline repro bundles
