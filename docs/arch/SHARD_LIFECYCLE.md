# Shard Lifecycle (MMO-2)

Shard lifecycle states are authoritative, deterministic, and logged.
They are an operational contract, not a gameplay mechanic.

## Canonical States

State codes are append-only within this major version:

- `1 INITIALIZING`
- `2 ACTIVE`
- `3 DRAINING`
- `4 FROZEN`
- `5 OFFLINE`

State meaning:

- INITIALIZING: Shard is constructing authoritative state.
- ACTIVE: Shard may advance simulation and accept intents.
- DRAINING: Shard is preparing handoff; no implicit escalation.
- FROZEN: Shard may be inspected or replayed but not advanced.
- OFFLINE: Shard is not authoritative.

## Transition Rules

Transitions MUST be explicit and logged.
They MUST occur at commit boundaries.

Allowed transitions:

- INITIALIZING -> ACTIVE, FROZEN, OFFLINE
- ACTIVE -> DRAINING, FROZEN, OFFLINE
- DRAINING -> ACTIVE, FROZEN, OFFLINE
- FROZEN -> INITIALIZING, ACTIVE, OFFLINE
- OFFLINE -> INITIALIZING, FROZEN

Invalid transitions MUST refuse explicitly and emit lifecycle events.

## Logging and Determinism

Lifecycle transitions are part of authoritative state:

- Every transition produces a lifecycle log entry.
- Lifecycle log hashes contribute to runtime hashes.
- Lifecycle logs are captured in checkpoints and restored on recovery.

## Invariants (Test Anchors)

- `MMO2-LIFECYCLE-003`: Lifecycle transitions are deterministic,
  commit-boundary only, and replayable from checkpoints.

