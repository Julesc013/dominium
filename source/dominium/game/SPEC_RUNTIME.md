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

## Performance budgets and profiling
Performance budgets and profiling contracts are defined in
`docs/SPEC_PERF_BUDGETS.md` and `docs/SPEC_PROFILING.md`. Budget enforcement MAY
degrade fidelity or cadence but MUST NOT change authoritative simulation
semantics.

## Snapshot boundary
UI/render MUST consume immutable snapshots only; snapshot construction MUST NOT
mutate authoritative state. See `docs/SPEC_FIDELITY_DEGRADATION.md`.

## Player continuity (UI)
View transitions and transit presentation are derived-only and must not block
the UI/render thread. See `docs/SPEC_PLAYER_CONTINUITY.md`.

## Session roles and authority
Session roles and authority modes are defined in `docs/SPEC_SESSIONS.md`. The
runtime MUST enforce role/authority validation and keep authority fixed for the
session lifetime.
In SERVER_AUTH mode, clients consume snapshots/deltas and must not advance
authoritative simulation ticks; any presentation state remains derived-only.

## QoS and assistance (non-sim)
QoS negotiation is defined in `docs/SPEC_QOS_ASSISTANCE.md`. QoS MAY adjust
snapshot cadence, detail, interest radius, and diagnostics rate only. QoS MUST
NOT affect tick progression, command ordering, or authoritative state.

## Determinism hooks
Authoritative simulation uses tick-first time and fixed-point space; see
`docs/SPEC_DETERMINISM.md`.

## Capabilities and epochs
SIM_CAPS/PERF_CAPS split and handshake validation are defined in
`docs/SPEC_CAPABILITIES.md`. Feature epoch gating for saves/replays/universe
bundles is defined in `docs/SPEC_FEATURE_EPOCH.md`.
