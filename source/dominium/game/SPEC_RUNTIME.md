# Runtime Spec

Status: draft
Version: 1

## Scope
This document defines runtime kernel boundaries and points to authoritative
contracts for non-blocking execution, derived work, and UI-facing snapshots.

## Non-blocking contract
The runtime UI/render thread MUST NOT block on IO, decompression, content
loading, or long computation. See `docs/SPEC_NO_MODAL_LOADING.md`.

## Derived work and budgets
Derived work MUST be budgeted, cancellable, and non-authoritative. See
`docs/SPEC_STREAMING_BUDGETS.md`.

## Snapshot boundary
UI/render MUST consume immutable snapshots only; snapshot construction MUST NOT
mutate authoritative state. See `docs/SPEC_FIDELITY_DEGRADATION.md`.

## Session roles and authority
Session roles and authority modes are defined in `docs/SPEC_SESSIONS.md`. The
runtime MUST enforce role/authority validation and keep authority fixed for the
session lifetime.

## Determinism hooks
Authoritative simulation uses tick-first time and fixed-point space; see
`docs/SPEC_DETERMINISM.md`.
