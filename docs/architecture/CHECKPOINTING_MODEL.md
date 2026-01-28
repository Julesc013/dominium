# Checkpointing Model (MMO-2)

A checkpoint is a committed, deterministic save container.
It exists to make crash recovery and rolling updates survivable
without changing simulation semantics.

## Definition

A checkpoint MUST be taken only at commit boundaries.

It MUST capture enough state to resume authoritatively using only:

- the checkpoint itself,
- the capability lockfile reference,
- the cross-shard log tail after the checkpoint position.

## Required Contents

The authoritative checkpoint container MUST include:

- checkpoint manifest:
  - `checkpoint_id`
  - `tick`
  - `trigger_reason`
  - capability and world definition hashes
  - cross-shard log position (`message_sequence`, `message_applied`)
- shard snapshots:
  - lifecycle state
  - capability/version metadata
  - domain state and hashes
  - budget state/snapshots
  - scale event logs
  - world checksums
- lifecycle log snapshot
- domain ownership table
- event log tail up to the checkpoint tick

Macro capsules and schedules are part of shard state and therefore
are checkpointed as part of the shard snapshot.

## Policy and Cadence

Checkpoint cadence MUST be policy-driven and deterministic.

Examples of allowed policies:

- every `N` ticks
- every `M` macro events
- before ownership transfer
- explicit manual checkpoints

Policy decisions MUST be replayable.

## Budget Integration

Checkpoint capture consumes snapshot budget.

If snapshot budget is insufficient:

- the checkpoint MUST refuse explicitly,
- a refusal event MUST be emitted,
- state MUST remain unchanged.

## Invariants (Test Anchors)

- `MMO2-CHECKPOINT-001`: Checkpoints are commit-boundary only,
  deterministic, and sufficient for authoritative recovery.
- `MMO2-LOG-006`: Checkpoints capture cross-shard log position and
  lifecycle log state needed to resume deterministically.

