Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Rolling Updates (MMO-2)

Rolling updates are an operational capability layered on top of the
deterministic simulator. They MUST NOT change simulation semantics.

## Mixed Versions

During a rolling update, shards MAY run different binaries.

Interaction is allowed only when capability baselines overlap.

If a shard lacks a required capability:

- it MUST refuse or defer deterministically,
- it MUST NOT reinterpret data.

## Upgrade Flow (Authoritative)

Upgrades MUST use checkpointed handoff:

1) take a committed checkpoint,
2) restart the shard on the new binary,
3) resync from checkpoint + log tail.

In-place mutation of live authoritative state is forbidden.

## Cross-Shard Safety

Cross-shard messaging and ownership transfer MUST be capability-aware.
Capability gaps MUST produce explicit refusals.

## Invariants (Test Anchors)

- `MMO2-ROLLING-004`: Mixed-version shards produce deterministic
  outcomes when capabilities overlap and explicit refusals otherwise.